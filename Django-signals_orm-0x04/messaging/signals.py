from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.utils import timezone

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