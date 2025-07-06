from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message
from django.urls import reverse
from django.test import Client

# Create your tests here.

class MessageReplyTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.client = Client()
        self.client.login(username='user1', password='testpass123')

    def test_reply_preview_with_deleted_message(self):
        """Test that reply previews show None for reply_content when replied-to message is deleted (Django SET_NULL behavior)"""
        # Create a message
        original_message = Message.objects.create(
            sender=self.user1,
            content='Original message content'
        )
        
        # Create a reply to that message
        reply_message = Message.objects.create(
            sender=self.user2,
            content='This is a reply',
            reply_to=original_message
        )
        
        # Delete the original message
        original_message.delete()
        
        # Access the chat page
        response = self.client.get(reverse('chat'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the reply message is in the context
        messages = response.context['messages']
        reply_found = False
        for message in messages:
            if message['id'] == reply_message.id:
                reply_found = True
                # After deletion, reply_to_id and reply_content should both be None
                self.assertIsNone(message['reply_to_id'])
                self.assertIsNone(message['reply_content'])
                break
        
        self.assertTrue(reply_found, "Reply message should be found in the response")

    def test_reply_preview_with_existing_message(self):
        """Test that reply previews show correct content when replied-to message exists"""
        # Create a message
        long_content = 'Original message content that is longer than 30 characters'
        original_message = Message.objects.create(
            sender=self.user1,
            content=long_content
        )
        
        # Create a reply to that message
        reply_message = Message.objects.create(
            sender=self.user2,
            content='This is a reply',
            reply_to=original_message
        )
        
        # Access the chat page
        response = self.client.get(reverse('chat'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the reply message is in the context
        messages = response.context['messages']
        reply_found = False
        for message in messages:
            if message['id'] == reply_message.id:
                reply_found = True
                # Check that reply_to_id is set and reply_content shows truncated content
                expected_truncated = long_content[:30] + ('...' if len(long_content) > 30 else '')
                self.assertEqual(message['reply_to_id'], original_message.id)
                self.assertEqual(message['reply_content'], expected_truncated)
                break
        
        self.assertTrue(reply_found, "Reply message should be found in the response")
