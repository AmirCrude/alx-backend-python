from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Message, Notification, MessageHistory
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.db import models


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
    # For testing, use the first user or create one
    try:
        user = User.objects.first()
        if not user:
            # Create a test user if none exists
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
        old_content = message.content  # Store old content for display
        message.content = request.POST.get('content')
        message.save()
        
        return redirect('message_history', message_id=message.id)
    
    return render(request, 'messaging/edit_message.html', {
        'message': message
    })

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    # Only allow sender or receiver to view history
    if message.sender != request.user and message.receiver != request.user:
        return redirect('inbox')
    
    history = message.history.all()
    
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'history': history
    })

@login_required
def delete_account(request):
    """View for users to delete their own account"""
    if request.method == 'POST':
        # Delete the user account
        user = request.user
        logout(request)  # Log out the user first
        user.delete()  # This will trigger the post_delete signal
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('login')
    
    return render(request, 'messaging/delete_account.html')

@login_required
def delete_user(request):  # CHANGED FROM delete_account to delete_user
    """View for users to delete their own account"""
    if request.method == 'POST':
        # Delete the user account
        user = request.user
        logout(request)  # Log out the user first
        user.delete()  # This will trigger the post_delete signal
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('login')
    
    return render(request, 'messaging/delete_account.html')


@login_required
def threaded_conversation(request, message_id=None):
    """
    Display a threaded conversation starting from a specific message.
    Uses prefetch_related and select_related for optimization.
    """
    if message_id:
        # Start from a specific message in the thread
        root_message = get_object_or_404(Message, id=message_id)
        # Ensure user has permission to view this conversation
        if root_message.sender != request.user and root_message.receiver != request.user:
            return redirect('inbox')
    else:
        # Get the latest conversation for the user
        latest_message = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).select_related('sender', 'receiver').first()
        
        if not latest_message:
            return render(request, 'messaging/threaded_conversation.html', {
                'error': 'No messages found.'
            })
        root_message = latest_message
    
    # Get all messages in this conversation thread
    # First, find the root of the thread (oldest parent)
    current = root_message
    while current.parent_message:
        current = current.parent_message
    root_message = current
    
    # Optimized query: get all messages in the thread with prefetching
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
    
    # Ensure user is part of the conversation
    if parent_message.sender != request.user and parent_message.receiver != request.user:
        return redirect('inbox')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create reply
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
    """
    Custom ORM method to get all conversations for a user with optimized queries.
    Returns a list of conversation threads with the latest message and reply count.
    """
    # Get all root messages (conversation starters) involving the user
    conversations = Message.objects.filter(
        Q(sender=user) | Q(receiver=user),
        parent_message__isnull=True  # Only root messages
    ).select_related('sender', 'receiver').prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
    ).annotate(
        reply_count=models.Count('replies'),
        last_activity=models.Max(
            models.Case(
                models.When(replies__isnull=False, then=models.F('replies__timestamp')),
                default=models.F('timestamp'),
                output_field=models.DateTimeField()
            )
        )
    ).order_by('-last_activity')
    
    return conversations


@login_required
def unread_inbox(request):
    """Display only unread messages using the custom manager"""
    unread_messages = Message.unread.unread_for_user(request.user)
    
    # Use .only() to optimize query - only get necessary fields
    unread_messages = unread_messages.select_related('sender').only(
        'id', 'content', 'timestamp', 'sender__username', 'edited'
    ).order_by('-timestamp')
    
    # Get unread count using the custom manager
    unread_count = Message.unread.unread_count_for_user(request.user)
    
    return render(request, 'messaging/unread_inbox.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_count,
    })
@login_required
def mark_as_read(request, message_id=None):
    """Mark messages as read using the custom manager"""
    if message_id:
        # Mark single message as read
        Message.unread.mark_as_read(request.user, [message_id])  # Changed to .unread
        messages.success(request, 'Message marked as read.')
    else:
        # Mark all unread messages as read
        count = Message.unread.mark_as_read(request.user)  # Changed to .unread
        messages.success(request, f'{count} messages marked as read.')
    
    return redirect('unread_inbox')

@login_required
def inbox_summary(request):
    """Display inbox summary with optimized queries"""
    # Get unread messages using custom manager with .only()
    unread_messages = Message.unread.unread_for_user(request.user).select_related(  # Changed to .unread.unread_for_user
        'sender'
    ).only('id', 'content', 'timestamp', 'sender__username').order_by('-timestamp')[:5]
    
    # Get recent messages (all messages, including read)
    recent_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').only(
        'id', 'content', 'timestamp', 'sender__username', 'receiver__username', 'read'
    ).order_by('-timestamp')[:10]
    
    # Get counts using optimized queries
    unread_count = Message.unread.unread_count_for_user(request.user)  # Changed to .unread
    total_count = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).count()
    
    return render(request, 'messaging/inbox_summary.html', {
        'unread_messages': unread_messages,
        'recent_messages': recent_messages,
        'unread_count': unread_count,
        'total_count': total_count,
    })