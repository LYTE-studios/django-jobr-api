from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import ChatRoom, Message


class MessageSerializer(serializers.ModelSerializer):

    """
    Serializer for the Message model, used to serialize message data for API responses.

    Fields:
        id (int): The unique identifier of the message.
        sender (UserSerializer): The user who sent the message.
        content (str): The content of the message.
        created_at (datetime): The timestamp when the message was created.
        modified_at (datetime): The timestamp when the message was last modified.
        read_by (UserSerializer): List of users who have read the message.
        is_sent_by_me (bool): A flag indicating whether the message was sent by the current authenticated user.

    Methods:
        validate_content(value):
            Validates the content of the message to ensure it is not empty or just whitespace.

        get_is_sent_by_me(obj):
            Checks whether the message was sent by the currently authenticated user.
    """
    read_by = UserSerializer(many=True, read_only=True)
    sender = UserSerializer(read_only=True)
    is_sent_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "sender", "content", "created_at", "modified_at", "read_by", "is_sent_by_me"]

    def validate_content(self, value):

        """
        Validate the content of the message.

        Args:
            value (str): The content of the message.

        Returns:
            str: The validated content of the message.

        Raises:
            serializers.ValidationError: If the message content is empty or consists of only whitespace.
        """
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value
    
    def get_is_sent_by_me(self, obj):

        """
        Check if the message was sent by the current authenticated user.

        Args:
            obj (Message): The message object being serialized.

        Returns:
            bool: True if the message was sent by the authenticated user, False otherwise.
        """
        request = self.context.get('request')

        if request:
            return obj.sender == request.user
        
        return False


class ChatRoomSerializer(serializers.ModelSerializer):

    """
    Serializer for the ChatRoom model.

    This serializer is used to convert ChatRoom model instances into JSON format and vice versa.
    It includes the `users` (a list of users in the chat room) and `messages` (a list of messages in the chat room).
    
    Fields:
        id (int): The unique identifier for the chat room.
        users (List[UserSerializer]): A list of user objects in the chat room, serialized using the UserSerializer.
        created_at (datetime): The timestamp of when the chat room was created.
        messages (List[MessageSerializer]): A list of message objects in the chat room, serialized using the MessageSerializer.
    """
    users = UserSerializer(many=True, read_only=True)

    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "users", "created_at", "messages"]
