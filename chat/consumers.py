import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile
import base64
import os
from django.conf import settings
import asyncio

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat_room'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            content = data['content']
            reply_to_id = data.get('reply_to_id')
            mentions = data.get('mentions', [])
            attachment_url = data.get('attachment')
            thumbnail_url = data.get('thumbnail')  # Get thumbnail URL from frontend
            sender = self.scope['user']

            message = await self.save_message(sender, content, reply_to_id, mentions, attachment_url, thumbnail_url)
            print(f"SAVED MESSAGE DEBUG - ID: {message.id}, Content: {content[:30]}..., Attachment: {attachment_url}, Thumbnail: {thumbnail_url}")

            # Add a short delay to ensure DB commit for replied-to message
            if reply_to_id:
                await asyncio.sleep(0.05)

            # Prepare reply preview info using async ORM access
            reply_content = None
            reply_attachment = None
            reply_attachment_type = None
            reply_thumbnail = None
            if reply_to_id:
                reply_content, reply_attachment, reply_attachment_type, reply_thumbnail = await self.get_reply_preview(reply_to_id)

            
            print("WS OUT:", {
                'id': message.id,
                'sender': sender.username,
                'content': content,
                'timestamp': message.timestamp.strftime('%Y-%m-%dT%H:%M'),
                'reply_to_id': reply_to_id,
                'reply_content': reply_content,
                'reply_attachment': reply_attachment,
                'reply_attachment_type': reply_attachment_type,
                'reply_thumbnail': reply_thumbnail,
                'mentions': mentions,
                'attachment': message.attachment.url if message.attachment else None,
                'thumbnail': message.thumbnail.url if message.thumbnail else None,
            })
            print("THUMBNAIL DEBUG - Message ID:", message.id)
            print("THUMBNAIL DEBUG - message.thumbnail:", message.thumbnail)
            print("THUMBNAIL DEBUG - message.thumbnail.url:", message.thumbnail.url if message.thumbnail else None)
            print("THUMBNAIL DEBUG - message.attachment:", message.attachment)
            print("THUMBNAIL DEBUG - Is PDF:", message.attachment.url.lower().endswith('.pdf') if message.attachment else False)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'sender': sender.username,
                        'content': content,
                        'timestamp': message.timestamp.strftime('%Y-%m-%dT%H:%M'),
                        'reply_to_id': reply_to_id,
                        'reply_content': reply_content,
                        'reply_attachment': reply_attachment,
                        'reply_attachment_type': reply_attachment_type,
                        'reply_thumbnail': reply_thumbnail,
                        'mentions': mentions,
                        'attachment': message.attachment.url if message.attachment else None,
                        'thumbnail': message.thumbnail.url if message.thumbnail else None,
                    }
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def delete_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'delete_message',
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def save_message(self, sender, content, reply_to_id, mentions, attachment_url, thumbnail_url=None):
        message = Message.objects.create(
            sender=sender,
            content=content,
            reply_to_id=reply_to_id if reply_to_id else None
        )
        if attachment_url:
            if attachment_url.startswith(settings.MEDIA_URL):
                attachment_url = attachment_url[len(settings.MEDIA_URL):]
            if attachment_url.startswith('/'):
                attachment_url = attachment_url[1:]
            message.attachment.name = attachment_url
        if thumbnail_url:
            if thumbnail_url.startswith(settings.MEDIA_URL):
                thumbnail_url = thumbnail_url[len(settings.MEDIA_URL):]
            if thumbnail_url.startswith('/'):
                thumbnail_url = thumbnail_url[1:]
            message.thumbnail.name = thumbnail_url
        message.save()
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                message.mentions.add(user)
            except User.DoesNotExist:
                pass
        return message

    @database_sync_to_async
    def get_reply_preview(self, reply_to_id):
        try:
            reply_msg = Message.objects.get(id=reply_to_id)
            reply_attachment = None
            reply_attachment_type = None
            reply_thumbnail = None
            if reply_msg.attachment:
                reply_attachment = reply_msg.attachment.url
                if reply_msg.attachment.url.lower().endswith('.pdf'):
                    reply_attachment_type = 'pdf'
                    reply_thumbnail = reply_msg.thumbnail.url if reply_msg.thumbnail else None
                elif reply_msg.attachment.url.lower().endswith(('.jpg', '.jpeg', '.png')):
                    reply_attachment_type = 'image'
                    reply_thumbnail = reply_msg.thumbnail.url if reply_msg.thumbnail else None
            # Robust reply_content logic
            if reply_msg.content.strip():
                reply_content = reply_msg.content[:30] + ('...' if len(reply_msg.content) > 30 else '')
            elif reply_attachment_type == 'image':
                reply_content = 'Photo'
            elif reply_attachment_type == 'pdf':
                reply_content = 'PDF Document'
            else:
                reply_content = ''
            return reply_content, reply_attachment, reply_attachment_type, reply_thumbnail
        except Message.DoesNotExist:
            return 'Message not found', None, None, None