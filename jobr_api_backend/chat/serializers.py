from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import ChatRoom, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "chatroom", "sender", "content", "timestamp"]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value


class ChatRoomSerializer(serializers.ModelSerializer):
    employer = UserSerializer(read_only=True) 
    employee = UserSerializer(read_only=True) 
    
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "employer", "employee", "created_at", "messages"]

    def validate(self, data):
        if data.get("employer") == data.get("employee"):
            raise serializers.ValidationError(
                {"employee": "Employer and employee cannot be the same user."}
            )
        return data
