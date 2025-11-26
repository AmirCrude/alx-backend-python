from django.contrib import admin
from .models import Message, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'content_preview', 'timestamp', 'read']
    list_filter = ['timestamp', 'read', 'sender', 'receiver']
    search_fields = ['sender__username', 'receiver__username', 'content']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message_preview', 'notification_type', 'created_at', 'read']
    list_filter = ['notification_type', 'created_at', 'read', 'user']
    search_fields = ['user__username', 'message__content']
    readonly_fields = ['created_at']
    
    def message_preview(self, obj):
        return obj.message.content[:50] + '...' if len(obj.message.content) > 50 else obj.message.content
    message_preview.short_description = 'Message'