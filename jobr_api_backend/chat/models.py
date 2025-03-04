from django.db import models

# from django.contrib.auth.models import User
from django.conf import settings

from vacancies.models import Vacancy


# Create your models here.
class ChatRoom(models.Model):
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_chatrooms",
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_chatrooms",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="chatrooms_vacancy", null=True, blank=True)
    def __str__(self):
        return f"ChatRoom {self.id} ({self.employer} - {self.employee})"


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
