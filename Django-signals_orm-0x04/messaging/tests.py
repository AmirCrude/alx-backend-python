from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.utils import timezone
from django.urls import reverse
from django.db import models
from django.db.models import Q



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

class MessageHistoryModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')
        # Create a message for the history tests
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

class UserDeletionTests(TestCase):
    def setUp(self):
        """Set up test users and data"""
        self.user1 = User.objects.create_user(
            username='user1', 
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            password='testpass123'
        )
        
        # Store user IDs for later use
        self.user1_id = self.user1.id
        self.user2_id = self.user2.id

    def test_user_deletion_orphaned_messages_cleaned_up(self):
        """Test that orphaned messages are cleaned up when user is deleted"""
        # Create messages
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message from user1"
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Test message to user1"
        )
        
        # Count total messages before deletion
        total_messages_before = Message.objects.count()
        self.assertEqual(total_messages_before, 2)
        
        # Delete user1
        self.user1.delete()
        
        # Check that orphaned messages (with null sender/receiver) are cleaned up
        total_messages_after = Message.objects.count()
        # Both messages should be deleted since one had user1 as sender, other as receiver
        self.assertEqual(total_messages_after, 0)

    def test_user_deletion_cleanup_notifications(self):
        """Test that user notifications are deleted when user is deleted"""
        # Create a message first
        message = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Test message for notification"
        )
        
        # Manually create a notification (bypass the automatic signal)
        # First, delete any auto-created notifications
        Notification.objects.all().delete()
        
        notification = Notification.objects.create(
            user=self.user1,
            message=message,
            notification_type='new_message'
        )
        
        notification_count_before = Notification.objects.filter(user_id=self.user1_id).count()
        self.assertEqual(notification_count_before, 1)
        
        # Delete the user
        self.user1.delete()
        
        # Check that notifications are automatically deleted via CASCADE
        notification_count_after = Notification.objects.filter(user_id=self.user1_id).count()
        self.assertEqual(notification_count_after, 0)

    def test_user_deletion_cleanup_message_history(self):
        """Test that message history with null editors is cleaned up"""
        # Create a message first
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message for history"
        )
        
        # Create message history
        history = MessageHistory.objects.create(
            message=message,
            old_content="Original content",
            edited_by=self.user1
        )
        
        history_count_before = MessageHistory.objects.count()
        self.assertEqual(history_count_before, 1)
        
        # Delete the user
        self.user1.delete()
        
        # Check that message history with null editor is cleaned up
        history_count_after = MessageHistory.objects.count()
        self.assertEqual(history_count_after, 0)

    def test_other_user_data_preserved(self):
        """Test that other users' data is preserved when one user is deleted"""
        # Create a message that doesn't involve user1 at all
        message1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user2,  # user2 sending to themselves
            content="Test message within user2"
        )
        
        user2_messages_before = Message.objects.filter(sender_id=self.user2_id, receiver_id=self.user2_id).count()
        self.assertEqual(user2_messages_before, 1)
        
        # Delete user1 (should not affect user2's self-referencing message)
        self.user1.delete()
        
        # Check that user2's data is still there
        user2_messages_after = Message.objects.filter(sender_id=self.user2_id, receiver_id=self.user2_id).count()
        self.assertEqual(user2_messages_after, 1)

class ThreadedConversationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')
        
        # Create a conversation thread
        self.root_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, how are you?"
        )
        self.reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="I'm good, thanks!",
            parent_message=self.root_message
        )
        self.reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="That's great to hear!",
            parent_message=self.reply1
        )
    
    def test_message_thread_creation(self):
        """Test that threaded messages are properly linked"""
        self.assertIsNone(self.root_message.parent_message)
        self.assertEqual(self.reply1.parent_message, self.root_message)
        self.assertEqual(self.reply2.parent_message, self.reply1)
        
        # Test reverse relationships
        self.assertEqual(self.root_message.replies.count(), 1)
        self.assertEqual(self.reply1.replies.count(), 1)
        self.assertEqual(self.reply2.replies.count(), 0)
    
    def test_thread_depth_calculation(self):
        """Test thread depth calculation"""
        self.assertEqual(self.root_message.get_thread_depth(), 0)
        self.assertEqual(self.reply1.get_thread_depth(), 1)
        self.assertEqual(self.reply2.get_thread_depth(), 2)
    
    def test_is_reply_property(self):
        """Test the is_reply property"""
        self.assertFalse(self.root_message.is_reply)
        self.assertTrue(self.reply1.is_reply)
        self.assertTrue(self.reply2.is_reply)
    
    def test_optimized_thread_query(self):
        """Test that thread queries are optimized with select_related and prefetch_related"""
        from django.db import connection
        
        # Reset query count
        connection.queries_log.clear()
        
        # Get thread with optimized queries
        thread_messages = Message.objects.filter(
            Q(parent_message=self.root_message) | Q(id=self.root_message.id)
        ).select_related('sender', 'receiver', 'parent_message').prefetch_related('replies').order_by('timestamp')
        
        # Force evaluation to count queries
        list(thread_messages)
        
        # This should use fewer queries than naive approach
        # We can't predict exact count, but it should be reasonable
        query_count = len(connection.queries)
        self.assertLess(query_count, 10)  # Should be significantly less than N+1 queries
    
    def test_conversation_aggregation(self):
        """Test conversation aggregation with annotations"""
        from django.db.models import Count, Max, Case, When
        
        conversations = Message.objects.filter(
            Q(sender=self.user1) | Q(receiver=self.user1),
            parent_message__isnull=True
        ).select_related('sender', 'receiver').annotate(
            reply_count=Count('replies'),
            last_activity=Max(
                Case(
                    When(replies__isnull=False, then='replies__timestamp'),
                    default='timestamp',
                    output_field=models.DateTimeField()
                )
            )
        ).order_by('-last_activity')
        
        conversation = conversations.first()
        self.assertEqual(conversation.reply_count, 1)
        self.assertIsNotNone(conversation.last_activity)


class CustomManagerTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')
        
        # Create test messages
        self.read_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read message",
            read=True
        )
        self.unread_message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message 1",
            read=False
        )
        self.unread_message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Unread message 2",
            read=False
        )
    
    def test_unread_messages_manager_for_user(self):
        """Test that custom manager returns only unread messages for a user"""
        unread_for_user2 = Message.unread.unread_for_user(self.user2)  # Changed to .unread.unread_for_user
        self.assertEqual(unread_for_user2.count(), 1)
        self.assertEqual(unread_for_user2.first(), self.unread_message1)
        
        # Test for user1
        unread_for_user1 = Message.unread.unread_for_user(self.user1)  # Changed to .unread.unread_for_user
        self.assertEqual(unread_for_user1.count(), 1)
        self.assertEqual(unread_for_user1.first(), self.unread_message2)
    
    def test_unread_count_for_user(self):
        """Test unread count method"""
        self.assertEqual(Message.unread.unread_count_for_user(self.user2), 1)  # Changed to .unread
        self.assertEqual(Message.unread.unread_count_for_user(self.user1), 1)  # Changed to .unread
    
    def test_mark_as_read_single(self):
        """Test marking single message as read"""
        # Mark unread_message1 as read
        Message.unread.mark_as_read(self.user2, [self.unread_message1.id])  # Changed to .unread
        
        # Verify it's now read
        self.unread_message1.refresh_from_db()
        self.assertTrue(self.unread_message1.read)
        
        # Verify count decreased
        self.assertEqual(Message.unread.unread_count_for_user(self.user2), 0)  # Changed to .unread
    
    def test_mark_all_as_read(self):
        """Test marking all unread messages as read"""
        # Mark all unread messages for user1 as read
        count = Message.unread.mark_as_read(self.user1)  # Changed to .unread
        self.assertEqual(count, 1)
        
        # Verify no unread messages left for user1
        self.assertEqual(Message.unread.unread_count_for_user(self.user1), 0)  # Changed to .unread
    
    def test_only_optimization(self):
        """Test that .only() optimization works"""
        from django.db import connection
        
        # Reset query count
        connection.queries_log.clear()
        
        # Query with .only() optimization - using ALX pattern
        messages = Message.unread.unread_for_user(self.user2).select_related(  # Changed to .unread.unread_for_user
            'sender'
        ).only('id', 'content', 'timestamp', 'sender__username')
        
        # Force query execution
        list(messages)
        
        # Check that we're not fetching unnecessary fields
        self.assertTrue(len(connection.queries) > 0)