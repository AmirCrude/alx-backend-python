from django.db import models

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        return self.filter(receiver=user, read=False)
    
    def unread_count_for_user(self, user):
        return self.filter(receiver=user, read=False).count()
    
    def mark_as_read(self, user, message_ids=None):
        queryset = self.filter(receiver=user, read=False)
        if message_ids:
            queryset = queryset.filter(id__in=message_ids)
        return queryset.update(read=True)