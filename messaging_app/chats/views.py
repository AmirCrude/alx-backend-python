from rest_framework import viewsets, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer


# -----------------------------
# Conversation ViewSet
# -----------------------------
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.AllowAny]  # Change to IsAuthenticated in real projects

    # Optional: Custom action to add participants
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        conversation.participants.add(user)
        conversation.save()
        return Response({"status": "participant added"})


# -----------------------------
# Message ViewSet
# -----------------------------
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]  # Change to IsAuthenticated in real projects

    # Optional: override create to attach sender automatically
    def perform_create(self, serializer):
        # Here, sender must be sent in request.data or you can use request.user
        sender_id = self.request.data.get("sender")
        if not sender_id:
            raise serializers.ValidationError({"sender": "This field is required."})
        try:
            sender = User.objects.get(user_id=sender_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"sender": "User not found."})

        serializer.save(sender=sender)
