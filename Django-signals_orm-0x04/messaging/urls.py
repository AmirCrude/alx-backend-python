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
]