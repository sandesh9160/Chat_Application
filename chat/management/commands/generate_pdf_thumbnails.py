from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from chat.models import Message
from pdf2image import convert_from_bytes
import io
import os

class Command(BaseCommand):
    help = 'Generate thumbnails for PDF messages that don\'t have thumbnails'

    def handle(self, *args, **options):
        # Get all messages with PDF attachments
        pdf_messages = Message.objects.filter(
            attachment__endswith='.pdf'
        ).exclude(
            thumbnail__isnull=False
        ).exclude(
            thumbnail=''
        )

        self.stdout.write(f"Found {pdf_messages.count()} PDF messages without thumbnails")

        for message in pdf_messages:
            try:
                # Check if attachment file exists
                if not message.attachment or not os.path.exists(message.attachment.path):
                    self.stdout.write(f"Attachment file not found for message {message.id}")
                    continue

                # Read the PDF file
                with open(message.attachment.path, 'rb') as f:
                    pdf_bytes = f.read()

                # Generate thumbnail
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, fmt='jpeg')
                if not images:
                    self.stdout.write(f"Could not convert PDF to image for message {message.id}")
                    continue

                # Convert RGBA to RGB if needed
                if images[0].mode == "RGBA":
                    images[0] = images[0].convert("RGB")
                # Save thumbnail
                thumb_io = io.BytesIO()
                images[0].save(thumb_io, format='JPEG')
                
                # Generate thumbnail filename
                base_name = os.path.splitext(os.path.basename(message.attachment.name))[0]
                thumb_filename = f"{base_name}_thumb.jpg"
                thumb_path = f"attachments/{thumb_filename}"

                # Save thumbnail file
                thumb_path = default_storage.save(thumb_path, ContentFile(thumb_io.getvalue()))
                
                # Update message with thumbnail
                message.thumbnail.name = thumb_path
                message.save()

                self.stdout.write(f"Generated thumbnail for message {message.id}: {thumb_path}")

            except Exception as e:
                self.stdout.write(f"Error processing message {message.id}: {str(e)}")

        self.stdout.write(self.style.SUCCESS("Thumbnail generation completed")) 