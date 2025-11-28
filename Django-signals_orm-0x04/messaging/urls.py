from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('send/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('temp-inbox/', views.temp_inbox, name='temp_inbox'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:message_id>/history/', views.message_history, name='message_history'),
    path('delete-account/', views.delete_user, name='delete_user'),
    # Threaded conversation URLs
    path('thread/<int:message_id>/', views.threaded_conversation, name='threaded_conversation'),
    path('thread/', views.threaded_conversation, name='threaded_conversation_root'),
    path('message/<int:message_id>/reply/', views.reply_to_message, name='reply_to_message'),
    # Unread messages URLs
    path('unread/', views.unread_inbox, name='unread_inbox'),
    path('mark-read/', views.mark_as_read, name='mark_as_read'),
    path('mark-read/<int:message_id>/', views.mark_as_read, name='mark_as_read_single'),
    path('summary/', views.inbox_summary, name='inbox_summary'),
]