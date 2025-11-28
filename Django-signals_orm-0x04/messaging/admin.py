from django.contrib import admin
from .models import Message, Notification, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    extra = 0
    readonly_fields = ['edited_by', 'edited_at', 'old_content']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'content_preview', 'timestamp', 'read', 'edited', 'last_edited']
    list_filter = ['timestamp', 'read', 'edited', 'sender', 'receiver']
    search_fields = ['sender__username', 'receiver__username', 'content']
    readonly_fields = ['timestamp', 'last_edited']
    inlines = [MessageHistoryInline]
    
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

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'old_content_preview', 'edited_by', 'edited_at']
    list_filter = ['edited_at', 'edited_by']
    search_fields = ['message__content', 'old_content', 'edited_by__username']
    readonly_fields = ['message', 'old_content', 'edited_by', 'edited_at']
    
    def old_content_preview(self, obj):
        return obj.old_content[:50] + '...' if len(obj.old_content) > 50 else obj.old_content
    old_content_preview.short_description = 'Old Content'
    
    def has_add_permission(self, request):
        return False