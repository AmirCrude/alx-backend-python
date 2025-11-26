from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.utils import timezone

class SignalTests(TestCase):
    def setUp(self):
        """Set up test users"""
        self.sender = User.objects.create_user(
            username='sender', 
            password='testpass123',
            email='sender@example.com'
        )
        self.receiver = User.objects.create_user(
            username='receiver', 
            password='testpass123',
            email='receiver@example.com'
        )
    
    def test_notification_created_on_new_message(self):
        """Test that a notification is automatically created when a new message is sent"""
        # Count initial notifications
        initial_notification_count = Notification.objects.count()
        
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!"
        )
        
        # Check that a notification was created
        final_notification_count = Notification.objects.count()
        self.assertEqual(final_notification_count, initial_notification_count + 1)
        
        # Verify the notification details
        notification = Notification.objects.last()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'new_message')
        self.assertFalse(notification.read)
    
    def test_no_notification_on_message_update(self):
        """Test that no notification is created when an existing message is updated"""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial message"
        )
        
        # Count notifications after creation
        notification_count_after_creation = Notification.objects.count()
        
        # Update the message
        message.content = "Updated message"
        message.read = True
        message.save()
        
        # Verify no new notification was created
        notification_count_after_update = Notification.objects.count()
        self.assertEqual(notification_count_after_update, notification_count_after_creation)
    
    def test_message_edit_history_created_on_content_change(self):
        """Test that message edit history is created when content is changed"""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message content"
        )
        
        # Verify no history initially
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(message.edited)
        self.assertIsNone(message.last_edited)
        
        # Update the message content
        message.content = "Updated message content"
        message.save()
        
        # Verify history was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        
        history = MessageHistory.objects.first()
        self.assertEqual(history.message, message)
        self.assertEqual(history.old_content, "Original message content")
        self.assertEqual(history.edited_by, self.sender)
        
        # Verify message edit tracking fields were updated
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertIsNotNone(message.last_edited)
    
    def test_no_history_created_when_non_content_fields_change(self):
        """Test that no history is created when non-content fields are updated"""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )
        
        # Update read status (non-content field)
        message.read = True
        message.save()
        
        # Verify no history was created
        self.assertEqual(MessageHistory.objects.count(), 0)
        
        # Verify edit tracking fields remain unchanged
        message.refresh_from_db()
        self.assertFalse(message.edited)
        self.assertIsNone(message.last_edited)
    
    def test_multiple_edits_create_multiple_history_entries(self):
        """Test that multiple edits create multiple history entries"""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="First version"
        )
        
        # First edit
        message.content = "Second version"
        message.save()
        
        # Second edit
        message.content = "Third version"
        message.save()
        
        # Verify two history entries
        self.assertEqual(MessageHistory.objects.count(), 2)
        
        # Verify history content is correct
        history_entries = MessageHistory.objects.all()
        self.assertEqual(history_entries[0].old_content, "Second version")
        self.assertEqual(history_entries[1].old_content, "First version")

class MessageHistoryModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')
        self.message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
    
    def test_message_history_creation(self):
        """Test message history model creation"""
        history = MessageHistory.objects.create(
            message=self.message,
            old_content="Previous content",
            edited_by=self.user1
        )
        
        self.assertEqual(str(history), f"History for Message {self.message.id} - {history.edited_at}")
        self.assertEqual(history.old_content, "Previous content")
        self.assertEqual(history.edited_by, self.user1)