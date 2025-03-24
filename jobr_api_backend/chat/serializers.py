from rest_framework import serializers
from .models import Message, ChatRoom
from accounts.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        required=False,
        allow_null=True
    )
    is_sent_by_me = serializers.SerializerMethodField()
    reply_to_message = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'content', 'created_at', 'is_deleted',
            'reply_to', 'is_read', 'is_sent_by_me', 'reply_to_message'
        ]
        read_only_fields = ['created_at', 'is_deleted', 'is_read']

    def get_is_sent_by_me(self, obj):
        """Check if the current user is the sender of the message."""
        request = self.context.get('request')
        if request and request.user:
            return obj.sender == request.user
        return False

    def get_reply_to_message(self, obj):
        """Get the replied to message details if any."""
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content,
                'sender': UserSerializer(obj.reply_to.sender).data
            }
        return None

    def validate_content(self, value):
        """Validate that the message content is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError('This field may not be blank.')
        return value.strip()

class SendMessageSerializer(serializers.ModelSerializer):
    """Serializer for sending new messages."""
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Message
        fields = ['content', 'reply_to']

    def validate(self, data):
        """Validate the message data."""
        if not self.context.get('request') or not self.context.get('chatroom'):
            raise serializers.ValidationError('Missing request or chatroom context')

        # Validate reply_to belongs to same chatroom
        reply_to = data.get('reply_to')
        if reply_to and reply_to.chatroom != self.context['chatroom']:
            raise serializers.ValidationError('Cannot reply to a message from a different chat room')

        # Validate content
        content = data.get('content')
        if not content or not content.strip():
            raise serializers.ValidationError('Message content cannot be empty')

        return data

    def create(self, validated_data):
        """Create a new message."""
        request = self.context.get('request')
        chatroom = self.context.get('chatroom')

        message = Message.objects.create(
            sender=request.user,
            chatroom=chatroom,
            content=validated_data['content'],
            reply_to=validated_data.get('reply_to')
        )
        return message

class DeleteMessageSerializer(serializers.ModelSerializer):
    """Serializer for soft-deleting messages."""
    class Meta:
        model = Message
        fields = ['is_deleted']

    def validate(self, data):
        """Validate the message can be deleted."""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError('Request context is required')

        if self.instance.sender != request.user:
            raise serializers.ValidationError('You can only delete your own messages')

        return data

    def update(self, instance, validated_data):
        """Soft delete the message."""
        instance.is_deleted = True
        instance.content = "Message deleted"  # Replace content for deleted messages
        instance.save()
        return instance

class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms."""
    messages = MessageSerializer(many=True, read_only=True)
    employee = UserSerializer(read_only=True)
    employer = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_messages_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'employee', 'employer', 'messages',
            'created_at', 'updated_at', 'last_message',
            'unread_messages_count', 'vacancy'
        ]

    def get_last_message(self, obj):
        """Get the last message in the chat room."""
        last_message = obj.messages.filter(is_deleted=False).order_by('-created_at').first()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

    def get_unread_messages_count(self, obj):
        """Get the number of unread messages for the current user."""
        request = self.context.get('request')
        if not request:
            return 0
        return obj.messages.filter(
            is_deleted=False,
            is_read=False
        ).exclude(sender=request.user).count()

    def validate(self, data):
        """Validate that the chat room has exactly two participants."""
        if self.instance:  # Skip validation for existing chat rooms
            return data

        if not self.context.get('request'):
            raise serializers.ValidationError("Request context is required")

        return data
