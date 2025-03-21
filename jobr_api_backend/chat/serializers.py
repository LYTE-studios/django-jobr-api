from rest_framework import serializers
from .models import Message, ChatRoom
from accounts.serializers import UserSerializer
from django.db.models import Q

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    is_sent_by_me = serializers.SerializerMethodField()

    content = serializers.SerializerMethodField()
    reply_to_message = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at', 'is_read', 'is_sent_by_me', 'is_deleted', 'reply_to', 'reply_to_message']
        read_only_fields = ['sender', 'created_at', 'is_read', 'is_deleted']

    def get_content(self, obj):
        return obj.display_content

    def get_reply_to_message(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.display_content,
                'sender': UserSerializer(obj.reply_to.sender).data
            }
        return None

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
    reply_to = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Message
        fields = ['content', 'reply_to']

    def validate_content(self, value):
        """
        Validate that the message content is not empty or whitespace.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty or contain only whitespace.")
        return value

    def validate_reply_to(self, value):
        """
        Validate that the replied-to message exists and is in the same chatroom.
        """
        if value:
            chatroom = self.context.get('chatroom')
            try:
                replied_message = Message.objects.get(id=value, chatroom=chatroom)
                return replied_message
            except Message.DoesNotExist:
                raise serializers.ValidationError("Reply message not found in this chat.")
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        chatroom = self.context.get('chatroom')
        
        if not request or not chatroom:
            raise serializers.ValidationError("Missing request or chatroom context")
        
        reply_to = validated_data.pop('reply_to', None)
        
        message = Message.objects.create(
            chatroom=chatroom,
            sender=request.user,
            content=validated_data['content'],
            reply_to=reply_to
        )
        
        # Update chatroom's updated_at timestamp
        chatroom.save()  # This will trigger the auto_now field
        
        return message

class DeleteMessageSerializer(serializers.Serializer):
    def validate(self, attrs):
        message = self.instance
        request = self.context.get('request')
        
        if not message:
            raise serializers.ValidationError("Message not found.")
        
        if message.sender != request.user:
            raise serializers.ValidationError("You can only delete your own messages.")
            
        return attrs

    def update(self, instance, validated_data):
        instance.delete_message(self.context['request'].user)
        return instance
