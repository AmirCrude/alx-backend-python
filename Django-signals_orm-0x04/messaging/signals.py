from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a notification when a new message is created.
    Only triggers when a new message is created (not on updates).
    """
    if created:
        # Create notification for the receiver
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='new_message'
        )
        print(f"✅ Notification created for {instance.receiver.username}")