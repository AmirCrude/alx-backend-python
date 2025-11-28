from django.db import models

class UnreadMessagesManager(models.Manager):
    """Custom manager for unread messages"""
    
    def unread_for_user(self, user):
        """Return unread messages for a specific user - matches ALX requirement"""
        return self.filter(receiver=user, read=False)
    
    def unread_count_for_user(self, user):
        """Return count of unread messages for a specific user"""
        return self.filter(receiver=user, read=False).count()
    
    def mark_as_read(self, user, message_ids=None):
        """Mark messages as read for a user"""
        queryset = self.filter(receiver=user, read=False)
        if message_ids:
            queryset = queryset.filter(id__in=message_ids)
        return queryset.update(read=True)