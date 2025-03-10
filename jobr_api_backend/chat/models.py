from django.db import models

# from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class ChatRoom(models.Model):

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chatroom_users",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom {self.id} ({[user.username for user in self.users.all()]})"

    def get_unread_messages(self, user):
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
        return f"Message {self.id} from {self.sender}"
