from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Message, Notification

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
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user)
    notifications = Notification.objects.filter(user=request.user)
    
    return render(request, 'messaging/inbox.html', {
        'received_messages': received_messages,
        'notifications': notifications
    })