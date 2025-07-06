from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from .models import Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pdf2image import convert_from_bytes
from PIL import Image
import io
import mimetypes

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            if ' ' in username:
                messages.error(request, 'Username cannot contain spaces')
                return render(request, 'register.html')
            validate_password(password)
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('chat')
        except IntegrityError:
            messages.error(request, 'Username already exists')
        except ValidationError as e:
            messages.error(request, e.messages[0])
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('chat')
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

@login_required
def chat(request):
    messages_qs = Message.objects.select_related('sender').prefetch_related('mentions').all().order_by('-timestamp')[:100]
    users = list(User.objects.exclude(id=request.user.id).values_list('username', flat=True))

    # Collect all reply_to_ids in the visible window
    reply_to_ids = set()
    for message in messages_qs:
        if message.reply_to_id:
            reply_to_ids.add(message.reply_to_id)
    # Fetch all replied-to messages in one query
    replied_messages = {m.id: m for m in Message.objects.filter(id__in=reply_to_ids)}

    message_data = []
    print('--- DEBUG: All message IDs in queryset:', [m.id for m in messages_qs])
    for message in messages_qs:
        reply_content = None
        reply_attachment = None
        reply_attachment_type = None
        if message.reply_to_id:
            print(f'--- DEBUG: Message {message.id} is a reply to {message.reply_to_id}')
            reply_msg = replied_messages.get(message.reply_to_id)
            if reply_msg:
                print(f'--- DEBUG: Found replied-to message {reply_msg.id}')
                # Robust reply_content logic for refresh (match consumer)
                if reply_msg.content.strip():
                    reply_content = reply_msg.content[:30] + ('...' if len(reply_msg.content) > 30 else '')
                elif reply_msg.attachment:
                    if reply_msg.attachment.url.lower().endswith('.pdf'):
                        reply_content = 'PDF Document'
                        reply_attachment_type = 'pdf'
                    elif reply_msg.attachment.url.lower().endswith(('.jpg', '.jpeg', '.png')):
                        reply_content = 'Photo'
                        reply_attachment_type = 'image'
                    reply_attachment = reply_msg.attachment.url
            else:
                print(f'--- DEBUG: Replied-to message {message.reply_to_id} NOT FOUND')
                reply_content = 'Message not found'
                reply_attachment = None
                reply_attachment_type = None
        message_data.append({
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%dT%H:%M'),  # ISO string for frontend formatting
            'attachment': message.attachment.url if message.attachment else None,
            'thumbnail': message.thumbnail.url if message.thumbnail else None,
            'mentions': [user.username for user in message.mentions.all()],
            'reply_to_id': message.reply_to_id,
            'reply_content': reply_content,
            'reply_attachment': reply_attachment,
            'reply_attachment_type': reply_attachment_type,
            'sender': message.sender.username,
        })

    # Debug: Print message data for replies
    for msg in message_data:
        if msg['reply_to_id']:
            print(f"DEBUG: Message {msg['id']} has reply_to_id: {msg['reply_to_id']}, reply_content: {msg['reply_content']}")
    
    return render(request, 'chat.html', {
        'messages': message_data[::-1],  # reverse to show oldest first
        'users': users,
        'user': request.user
    })

@login_required
def mention_usernames(request):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = [s.get_decoded().get('_auth_user_id') for s in sessions if s.get_decoded().get('_auth_user_id')]
    users = User.objects.filter(id__in=uid_list).exclude(id=request.user.id).values_list('username', flat=True)
    return JsonResponse(list(users), safe=False)

@login_required
@require_POST
def delete_message(request, msg_id):
    try:
        msg = Message.objects.get(id=msg_id, sender=request.user)
        msg.delete()
        # Notify via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_room',
            {
                'type': 'delete_message',
                'message_id': msg_id
            }
        )
        return JsonResponse({'success': True})
    except Message.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'}, status=404)

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
@require_POST
def upload_attachment(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file provided'}, status=400)
    if file.content_type not in ['image/jpeg', 'image/png', 'application/pdf']:
        return JsonResponse({'error': 'Invalid file type'}, status=400)
    if file.size > 5 * 1024 * 1024:  # 5MB limit
        return JsonResponse({'error': 'File too large'}, status=400)

    filename = f'attachment_{request.user.id}_{os.urandom(8).hex()}{os.path.splitext(file.name)[1]}'
    file_path = default_storage.save(f'attachments/{filename}', ContentFile(file.read()))
    file_url = default_storage.url(file_path)

    # If PDF, generate thumbnail
    thumbnail_url = None
    if file.content_type == 'application/pdf':
        file.seek(0)
        images = convert_from_bytes(file.read(), first_page=1, last_page=1, fmt='jpeg')
        if images:
            thumb_io = io.BytesIO()
            images[0].save(thumb_io, format='JPEG')
            thumb_filename = filename.replace('.pdf', '_thumb.jpg')
            thumb_path = default_storage.save(f'attachments/{thumb_filename}', ContentFile(thumb_io.getvalue()))
            thumbnail_url = default_storage.url(thumb_path)

    return JsonResponse({'url': file_url, 'thumbnail': thumbnail_url})

@login_required
def download_attachment(request, message_id):
    """Download attachment from a message"""
    try:
        message = Message.objects.get(id=message_id)
        if not message.attachment:
            raise Http404("No attachment found")
        
        # Check if user has permission to download (either sender or any authenticated user)
        # For a chat app, we'll allow any authenticated user to download
        if not request.user.is_authenticated:
            raise Http404("Authentication required")
        
        file_path = message.attachment.path
        if not os.path.exists(file_path):
            raise Http404("File not found")
        
        # Get file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Read file and create response
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            response['Content-Length'] = file_size
            return response
            
    except Message.DoesNotExist:
        raise Http404("Message not found")
    except Exception as e:
        raise Http404(f"Download failed: {str(e)}")

@login_required
def attachment_preview(request, message_id):
    """Show large preview of attachment with download options"""
    try:
        message = Message.objects.get(id=message_id)
        if not message.attachment:
            raise Http404("No attachment found")
        
        # Check if user has permission to view
        if not request.user.is_authenticated:
            raise Http404("Authentication required")
        
        file_path = message.attachment.path
        if not os.path.exists(file_path):
            raise Http404("File not found")
        
        # Get file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Determine file type
        content_type, _ = mimetypes.guess_type(file_path)
        is_image = content_type and content_type.startswith('image/')
        is_pdf = content_type == 'application/pdf'
        
        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        context = {
            'message': message,
            'attachment_url': message.attachment.url,
            'file_name': file_name,
            'file_size': size_str,
            'is_image': is_image,
            'is_pdf': is_pdf,
            'content_type': content_type,
            'sender': message.sender.username,
            'timestamp': message.timestamp,
        }
        
        return render(request, 'attachment_preview.html', context)
        
    except Message.DoesNotExist:
        raise Http404("Message not found")
    except Exception as e:
        raise Http404(f"Preview failed: {str(e)}")
