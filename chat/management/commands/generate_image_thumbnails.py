from django.core.management.base import BaseCommand
from chat.models import Message
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
import io
import os

class Command(BaseCommand):
    help = 'Generate thumbnails for existing image attachments'

    def handle(self, *args, **options):
        # Get all messages with image attachments that don't have thumbnails
        messages = Message.objects.filter(
            attachment__isnull=False,
            thumbnail__isnull=True
        ).exclude(attachment='')
        
        image_messages = []
        for message in messages:
            if message.attachment and message.attachment.url.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_messages.append(message)
        
        self.stdout.write(f"Found {len(image_messages)} image messages without thumbnails")
        
        for message in image_messages:
            try:
                # Check if attachment file exists
                if not os.path.exists(message.attachment.path):
                    self.stdout.write(f"Warning: Attachment file not found for message {message.id}: {message.attachment.path}")
                    continue
                
                # Open and create thumbnail
                with open(message.attachment.path, 'rb') as f:
                    img = Image.open(f)
                    
                    # Convert RGBA to RGB if needed
                    if img.mode == "RGBA":
                        img = img.convert("RGB")
                    # Calculate thumbnail size (max 200x200 while maintaining aspect ratio)
                    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                    
                    # Save thumbnail
                    thumb_io = io.BytesIO()
                    img.save(thumb_io, format='JPEG', quality=85)
                    
                    # Generate thumbnail filename
                    original_filename = os.path.basename(message.attachment.name)
                    thumb_filename = original_filename.replace(os.path.splitext(original_filename)[1], '_thumb.jpg')
                    thumb_path = f'attachments/{thumb_filename}'
                    
                    # Save thumbnail file
                    default_storage.save(thumb_path, ContentFile(thumb_io.getvalue()))
                    
                    # Update message with thumbnail
                    message.thumbnail.name = thumb_path
                    message.save()
                    
                    self.stdout.write(f"Generated thumbnail for message {message.id}: {thumb_path}")
                    
            except Exception as e:
                self.stdout.write(f"Error generating thumbnail for message {message.id}: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS('Image thumbnail generation completed')) 