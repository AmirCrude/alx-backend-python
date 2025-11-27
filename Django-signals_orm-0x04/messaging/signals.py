from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a notification when a new message is created.
    Only triggers when a new message is created (not on updates).
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='new_message'
        )
        print(f"✅ Notification created for {instance.receiver.username}")

@receiver(pre_save, sender=Message)
def log_message_edit_history(sender, instance, **kwargs):
    """
    Signal receiver that logs message edit history before saving changes.
    Only triggers when an existing message is being updated and content changed.
    """
    if instance.pk:  # Only for existing instances (updates)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Content changed
                # Log the old content to history
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content,
                    edited_by=instance.sender  # Assuming sender is editing
                )
                # Update edit tracking fields
                instance.edited = True
                instance.last_edited = timezone.now()
                print(f"📝 Message edit history logged for message {instance.id}")
        except Message.DoesNotExist:
            pass  # Message doesn't exist yet (shouldn't happen in pre_save)

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal receiver that cleans up all user-related data when a user is deleted.
    Since we use SET_NULL for some foreign keys, we need to clean up the orphaned data.
    """
    user_id = instance.id
    username = instance.username
    
    print(f"🧹 Cleaning up data for deleted user: {username} (ID: {user_id})")
    
    # Clean up messages where sender or receiver is now NULL (due to SET_NULL)
    # These are messages where the user was either sender or receiver
    null_sender_messages = Message.objects.filter(sender__isnull=True)
    null_receiver_messages = Message.objects.filter(receiver__isnull=True)
    
    # Combine and delete orphaned messages
    orphaned_messages = null_sender_messages | null_receiver_messages
    message_count = orphaned_messages.count()
    orphaned_messages.delete()
    print(f"   Deleted {message_count} orphaned messages")
    
    # Notifications are automatically deleted via CASCADE, so we don't need to handle them
    
    # Clean up message history where edited_by is now NULL
    null_editor_history = MessageHistory.objects.filter(edited_by__isnull=True)
    history_count = null_editor_history.count()
    null_editor_history.delete()
    print(f"   Deleted {history_count} orphaned message history entries")
    
    print(f"✅ Cleanup completed for user: {username}")