from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import ChatRoom, Message


class MessageSerializer(serializers.ModelSerializer):
    read_by = UserSerializer(many=True, read_only=True)
    sender = UserSerializer(read_only=True)
    is_sent_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "sender", "content", "created_at", "modified_at", "read_by", "is_sent_by_me"]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value
    
    def get_is_sent_by_me(self, obj):
        request = self.context.get('request')

        if request:
            return obj.sender == request.user
        
        return False


class ChatRoomSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "users", "created_at", "messages"]
