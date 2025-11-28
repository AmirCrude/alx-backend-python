from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Prefetch, Q, Count, Max, Case, When
from django.db import models
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Message, Notification, MessageHistory

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inbox')
    else:
        form = AuthenticationForm()
    return render(request, 'messaging/login.html', {'form': form})

# Temporary view for easy testing - allows any user to access
def temp_inbox(request):
    """Temporary inbox view that doesn't require login for testing"""
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        
        received_messages = Message.objects.filter(receiver=user)
        sent_messages = Message.objects.filter(sender=user)
        notifications = Notification.objects.filter(user=user)
        
        return render(request, 'messaging/inbox.html', {
            'received_messages': received_messages,
            'sent_messages': sent_messages,
            'notifications': notifications
        })
    except Exception as e:
        return render(request, 'messaging/inbox.html', {
            'error': f'Setup error: {e}'
        })

@login_required
@cache_page(60)
def inbox(request):
    """Proper inbox view that requires login"""
    received_messages = Message.objects.filter(receiver=request.user)
    sent_messages = Message.objects.filter(sender=request.user)
    notifications = Notification.objects.filter(user=request.user)
    
    return render(request, 'messaging/inbox.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'notifications': notifications
    })

@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content = request.POST.get('content')
        
        try:
            receiver = User.objects.get(username=receiver_username)
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            return redirect('inbox')
        except User.DoesNotExist:
            return render(request, 'messaging/send_message.html', {
                'error': 'User not found'
            })
    
    return render(request, 'messaging/send_message.html')

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    if request.method == 'POST':
        message.content = request.POST.get('content')
        message.save()
        return redirect('message_history', message_id=message.id)
    
    return render(request, 'messaging/edit_message.html', {
        'message': message
    })

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user and message.receiver != request.user:
        return redirect('inbox')
    
    history = message.history.all()
    
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'history': history
    })

@login_required
def delete_user(request):
    """View for users to delete their own account"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('login')
    
    return render(request, 'messaging/delete_account.html')

@login_required
@cache_page(60)
def threaded_conversation(request, message_id=None):
    """Display a threaded conversation starting from a specific message"""
    if message_id:
        root_message = get_object_or_404(Message, id=message_id)
        if root_message.sender != request.user and root_message.receiver != request.user:
            return redirect('inbox')
    else:
        latest_message = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).select_related('sender', 'receiver').first()
        
        if not latest_message:
            return render(request, 'messaging/threaded_conversation.html', {
                'error': 'No messages found.'
            })
        root_message = latest_message
    
    current = root_message
    while current.parent_message:
        current = current.parent_message
    root_message = current
    
    thread_messages = Message.objects.filter(
        Q(parent_message=root_message) | Q(id=root_message.id)
    ).select_related('sender', 'receiver', 'parent_message').prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver').order_by('timestamp'))
    ).order_by('timestamp')
    
    return render(request, 'messaging/threaded_conversation.html', {
        'root_message': root_message,
        'thread_messages': thread_messages,
    })

@login_required
def reply_to_message(request, message_id):
    """View to reply to a specific message"""
    parent_message = get_object_or_404(Message, id=message_id)
    
    if parent_message.sender != request.user and parent_message.receiver != request.user:
        return redirect('inbox')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            reply = Message.objects.create(
                sender=request.user,
                receiver=parent_message.sender if request.user != parent_message.sender else parent_message.receiver,
                content=content,
                parent_message=parent_message
            )
            return redirect('threaded_conversation', message_id=parent_message.id)
    
    return render(request, 'messaging/reply_message.html', {
        'parent_message': parent_message,
    })

def get_user_conversations(user):
    """Custom ORM method to get all conversations for a user with optimized queries"""
    conversations = Message.objects.filter(
        Q(sender=user) | Q(receiver=user),
        parent_message__isnull=True
    ).select_related('sender', 'receiver').prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
    ).annotate(
        reply_count=Count('replies'),
        last_activity=Max(
            Case(
                When(replies__isnull=False, then=models.F('replies__timestamp')),
                default=models.F('timestamp'),
                output_field=models.DateTimeField()
            )
        )
    ).order_by('-last_activity')
    
    return conversations

@login_required
@cache_page(60)
def unread_inbox(request):
    """Display only unread messages using the custom manager"""
    unread_messages = Message.unread.unread_for_user(request.user)
    
    unread_messages = unread_messages.select_related('sender').only(
        'id', 'content', 'timestamp', 'sender__username', 'edited'
    ).order_by('-timestamp')
    
    unread_count = Message.unread.unread_count_for_user(request.user)
    
    return render(request, 'messaging/unread_inbox.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_count,
    })

@login_required
def mark_as_read(request, message_id=None):
    """Mark messages as read using the custom manager"""
    if message_id:
        Message.unread.mark_as_read(request.user, [message_id])
        messages.success(request, 'Message marked as read.')
    else:
        count = Message.unread.mark_as_read(request.user)
        messages.success(request, f'{count} messages marked as read.')
    
    return redirect('unread_inbox')

@login_required
@cache_page(60)
def inbox_summary(request):
    """Display inbox summary with optimized queries"""
    unread_messages = Message.unread.unread_for_user(request.user).select_related(
        'sender'
    ).only('id', 'content', 'timestamp', 'sender__username').order_by('-timestamp')[:5]
    
    recent_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').only(
        'id', 'content', 'timestamp', 'sender__username', 'receiver__username', 'read'
    ).order_by('-timestamp')[:10]
    
    unread_count = Message.unread.unread_count_for_user(request.user)
    total_count = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).count()
    
    return render(request, 'messaging/inbox_summary.html', {
        'unread_messages': unread_messages,
        'recent_messages': recent_messages,
        'unread_count': unread_count,
        'total_count': total_count,
    })

@login_required
def cache_test(request):
    """Test view to demonstrate caching functionality"""
    cache_key = f'user_{request.user.id}_message_count'
    message_count = cache.get(cache_key)
    
    if message_count is None:
        message_count = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).count()
        cache.set(cache_key, message_count, 60)
        cache_source = 'Calculated and cached'
    else:
        cache_source = 'Retrieved from cache'
    
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render(request, 'messaging/cache_test.html', {
        'message_count': message_count,
        'cache_source': cache_source,
        'current_time': current_time,
        'cache_key': cache_key,
    })

def clear_cache_test(request):
    """Clear the cache for testing"""
    cache_key = f'user_{request.user.id}_message_count'
    cache.delete(cache_key)
    messages.success(request, 'Cache cleared for message count')
    return redirect('cache_test')