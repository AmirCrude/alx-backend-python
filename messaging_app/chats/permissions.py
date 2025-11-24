from rest_framework import permissions
from chats.models import Conversation # Assumes Conversation model is accessible here

class IsParticipantOfConversation(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        # Allow SAFE_METHODS (GET, HEAD, OPTIONS) only if the user is a participant
        if request.method in permissions.SAFE_METHODS:
            return self._is_participant(request.user, obj)

        # Allow CUD methods (POST, PUT, DELETE) only if the user is a participant
        return self._is_participant(request.user, obj)

    def has_permission(self, request, view):
        # Global permission check for list views (e.g., POST/GET list)
        # Allows only authenticated users, fulfilling part of the requirement
        return request.user and request.user.is_authenticated
    
    def _is_participant(self, user, obj):
        if isinstance(obj, Conversation):
            conversation = obj
        elif hasattr(obj, 'conversation'):
            # If obj is a Message, get its related conversation
            conversation = obj.conversation
        else:
            return False
        
        # Check if the user is in the participants list of the conversation
        return conversation.participants.filter(pk=user.pk).exists()