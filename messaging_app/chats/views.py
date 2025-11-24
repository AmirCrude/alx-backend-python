from rest_framework import viewsets, permissions, filters, serializers, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer
from .permissions import IsParticipantOfConversation


# -----------------------------
# Conversation ViewSet
# -----------------------------
class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    
    def get_queryset(self):
        """
        Return only conversations where the current user is a participant
        """
        return Conversation.objects.filter(participants=self.request.user)
    
    def perform_create(self, serializer):
        """
        Automatically add the current user as a participant when creating a conversation
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    # Optional: Custom action to add participants
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsParticipantOfConversation])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            # ✅ EXPLICITLY RETURNING HTTP_403_FORBIDDEN
            return Response({"error": "User not found"}, status=status.HTTP_403_FORBIDDEN)

        conversation.participants.add(user)
        conversation.save()
        return Response({"status": "participant added"})


# -----------------------------
# Message ViewSet (UPDATED FOR NESTED ROUTER)
# -----------------------------
class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    
    def get_queryset(self):
        """
        Return only messages from conversations where the current user is a participant
        Handle both nested (via conversation_pk) and non-nested access
        """
        queryset = Message.objects.filter(conversation__participants=self.request.user)
        
        # If accessed via nested router (conversation-messages), filter by conversation
        conversation_pk = self.kwargs.get('conversation_pk')
        if conversation_pk is not None:
            queryset = queryset.filter(conversation_id=conversation_pk)
            
        return queryset
    
    def perform_create(self, serializer):
        """
        Ensure the sender is set to the current user and handle conversation assignment
        """
        # If creating via nested URL, get conversation from URL parameter
        conversation_pk = self.kwargs.get('conversation_pk')
        if conversation_pk:
            try:
                conversation = Conversation.objects.get(pk=conversation_pk)
                # Check if user is a participant
                if self.request.user not in conversation.participants.all():
                    # ✅ EXPLICITLY RAISING PermissionDenied WHICH RETURNS HTTP_403_FORBIDDEN
                    raise permissions.PermissionDenied("You are not a participant of this conversation")
                serializer.save(sender=self.request.user, conversation=conversation)
            except Conversation.DoesNotExist:
                raise serializers.ValidationError({"conversation": "Conversation not found"})
        else:
            # If creating via non-nested URL, use conversation from request data
            conversation = serializer.validated_data.get('conversation')
            if not conversation:
                raise serializers.ValidationError({"conversation": "This field is required"})
            
            # Check if user is a participant
            if self.request.user not in conversation.participants.all():
                # ✅ EXPLICITLY RAISING PermissionDenied WHICH RETURNS HTTP_403_FORBIDDEN
                raise permissions.PermissionDenied("You are not a participant of this conversation")
            
            serializer.save(sender=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Override update to ensure only participants can update messages
        """
        # This will automatically check object permissions via IsParticipantOfConversation
        # which returns HTTP_403_FORBIDDEN if user is not a participant
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to ensure only participants can delete messages
        """
        # This will automatically check object permissions via IsParticipantOfConversation
        # which returns HTTP_403_FORBIDDEN if user is not a participant
        return super().destroy(request, *args, **kwargs)


# -----------------------------
# User ViewSet
# -----------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Users can only see their own profile by default
        """
        if self.action == 'list':
            # For listing, you might want to restrict or allow based on your needs
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)