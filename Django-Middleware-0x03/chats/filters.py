import django_filters
from django.utils import timezone
from .models import Message, Conversation

class MessageFilter(django_filters.FilterSet):
    """
    Filter class for messages to retrieve conversations with specific users or within time ranges
    """
    
    # Filter by specific user (participant in conversation)
    user = django_filters.NumberFilter(
        field_name='conversation__participants',
        lookup_expr='exact',
        label='Filter by user ID (participant in conversation)'
    )
    
    # Filter by username
    username = django_filters.CharFilter(
        field_name='conversation__participants__username',
        lookup_expr='icontains',
        label='Filter by username'
    )
    
    # Filter by time range - after specific date
    after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        label='Messages sent after this datetime'
    )
    
    # Filter by time range - before specific date
    before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        label='Messages sent before this datetime'
    )
    
    # Filter by today's messages
    today = django_filters.BooleanFilter(
        method='filter_today',
        label='Messages from today'
    )
    
    # Filter by conversation
    conversation = django_filters.NumberFilter(
        field_name='conversation__conversation_id',
        lookup_expr='exact',
        label='Filter by conversation ID'
    )
    
    class Meta:
        model = Message
        fields = ['user', 'username', 'after', 'before', 'today', 'conversation']
    
    def filter_today(self, queryset, name, value):
        """
        Custom filter for today's messages
        """
        if value:
            today = timezone.now().date()
            return queryset.filter(sent_at__date=today)
        return queryset