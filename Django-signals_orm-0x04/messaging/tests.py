from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

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
    
    def test_multiple_messages_create_multiple_notifications(self):
        """Test that multiple messages create multiple notifications"""
        # Create first message
        message1 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="First message"
        )
        
        # Create second message
        message2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Second message"
        )
        
        # Verify two notifications were created
        self.assertEqual(Notification.objects.count(), 2)
        
        # Verify each notification is for the correct message
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0].message, message2)  # Most recent first
        self.assertEqual(notifications[1].message, message1)

class ModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')
    
    def test_message_creation(self):
        """Test message model creation and string representation"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message content"
        )
        
        self.assertEqual(str(message), "From user1 to user2: Test message content")
        self.assertFalse(message.read)
    
    def test_notification_creation(self):
        """Test notification model creation and string representation"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message for notification"
        )
        
        notification = Notification.objects.create(
            user=self.user2,
            message=message,
            notification_type='new_message'
        )
        
        expected_str = "Notification for user2: Test message for notification"
        self.assertEqual(str(notification), expected_str)
        self.assertFalse(notification.read)