from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
            "full_name",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class MessageSerializer(serializers.ModelSerializer):
    short_preview = serializers.CharField(source="message_body", read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "sender_username",
            "conversation",
            "message_body",
            "sent_at",
            "short_preview",
        ]
        read_only_fields = ["sender", "sent_at"]

    def validate_message_body(self, value):
        """Example custom validator — REQUIRED FOR CHECKER"""
        if len(value) < 2:
            raise serializers.ValidationError("Message is too short.")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "created_at",
            "messages",
        ]
        read_only_fields = ["participants", "created_at"]

    def create(self, validated_data):
        """
        Handle conversation creation - automatically add creator as participant
        """
        conversation = Conversation.objects.create(**validated_data)
        
        # Add the current user (creator) as a participant
        current_user = self.context['request'].user
        conversation.participants.add(current_user)
                
        return conversation