from django.db import models

# from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class ChatRoom(models.Model):

    """
    Represents a chat room that can have multiple users and messages.

    Attributes:
        users (ManyToManyField): The users that are part of the chat room.
        created_at (DateTimeField): The date and time when the chat room was created.
    
    Methods:
        __str__(self): Returns a string representation of the chat room, including the user names.
        get_unread_messages(self, user): Returns unread messages for a specific user.
    """


    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chatroom_users",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        """
        Returns a string representation of the chat room, listing the users in the chat room.

        Returns:
            str: The string representation of the chat room.
        """
        return f"ChatRoom {self.id} ({[user.username for user in self.users.all()]})"

    def get_unread_messages(self, user):

        """
        Returns the unread messages for a specific user in the chat room.

        This method annotates the messages with a boolean indicating whether they have been read 
        by the specified user and filters them to return only unread messages.

        Args:
            user (User): The user for whom the unread messages are being retrieved.

        Returns:
            QuerySet: A queryset of unread messages for the specified user.
        """

        from django.db.models import Exists, OuterRef

        return self.messages.annotate(
            is_read=Exists(
                Message.objects.filter(
                    pk=OuterRef('pk'), 
                    read_by=user
                )
            )
        ).filter(is_read=False)

class Message(models.Model):

    """
    Represents a message in a chat room sent by a user.

    Attributes:
        chatroom (ForeignKey): The chat room to which the message belongs.
        sender (ForeignKey): The user who sent the message.
        content (TextField): The content of the message.
        created_at (DateTimeField): The date and time when the message was created.
        modified_at (DateTimeField): The date and time when the message was last modified.
        read_by (ManyToManyField): The users who have read the message.
    
    Methods:
        __str__(self): Returns a string representation of the message, including the sender's username.
    """

    chatroom = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="read_messages", blank=True
    )            

    def __str__(self):

        """
        Returns a string representation of the message, including the sender's username.

        Returns:
            str: The string representation of the message.
        """
        
        return f"Message {self.id} from {self.sender}"
