from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    last_edited = models.DateTimeField(null=True, blank=True)
    
    # Threading: self-referential foreign key for replies
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['parent_message', 'timestamp']),
            models.Index(fields=['sender', 'receiver', 'timestamp']),
        ]
    
    def __str__(self):
        sender_name = self.sender.username if self.sender else '[deleted user]'
        receiver_name = self.receiver.username if self.receiver else '[deleted user]'
        return f"From {sender_name} to {receiver_name}: {self.content[:50]}"
    
    def get_thread_depth(self):
        """Calculate how deep this message is in a thread"""
        depth = 0
        current = self
        while current.parent_message:
            depth += 1
            current = current.parent_message
        return depth
    
    @property
    def is_reply(self):
        """Check if this message is a reply to another message"""
        return self.parent_message is not None

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, default='new_message')
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        user_name = self.user.username if self.user else '[deleted user]'
        return f"Notification for {user_name}: {self.message.content[:50]}"

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    edited_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message histories"
    
    def __str__(self):
        editor_name = self.edited_by.username if self.edited_by else '[deleted user]'
        return f"History for Message {self.message.id} - {self.edited_at}"