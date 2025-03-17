from rest_framework import serializers
from .models import Message, ChatRoom
from accounts.serializers import UserSerializer
from django.db.models import Q

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    is_sent_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at', 'is_read', 'is_sent_by_me']
        read_only_fields = ['sender', 'created_at', 'is_read']

    def get_is_sent_by_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False

    def validate_content(self, value):
        """
        Validate that the message content is not empty or whitespace.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty or contain only whitespace.")
        return value

class ChatRoomSerializer(serializers.ModelSerializer):
    employee = UserSerializer(read_only=True)
    employer = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    unread_messages_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'employee', 'employer', 'vacancy', 'created_at', 'updated_at', 'messages', 'unread_messages_count', 'last_message']
        read_only_fields = ['created_at', 'updated_at']

    def get_unread_messages_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.messages.filter(
                ~Q(sender=request.user),
                is_read=False
            ).count()
        return 0

    def get_last_message(self, obj):
        last_message = obj.messages.first()  # Using first() since messages are ordered by -created_at
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

class SendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content']

    def validate_content(self, value):
        """
        Validate that the message content is not empty or whitespace.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty or contain only whitespace.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        chatroom = self.context.get('chatroom')
        
        if not request or not chatroom:
            raise serializers.ValidationError("Missing request or chatroom context")
        
        message = Message.objects.create(
            chatroom=chatroom,
            sender=request.user,
            content=validated_data['content']
        )
        
        # Update chatroom's updated_at timestamp
        chatroom.save()  # This will trigger the auto_now field
        
        return message
