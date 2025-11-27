from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Message, Notification, MessageHistory
from django.contrib import messages


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


# ... (keep all existing views above) ...

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