from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from vacancies.models import Vacancy

class ChatRoom(models.Model):
    """
    Represents a chat room between an employee and an employer.
    
    Attributes:
        employee (ForeignKey): Reference to the employee user.
        employer (ForeignKey): Reference to the employer user.
        vacancy (ForeignKey): Reference to the vacancy being discussed.
        created_at (DateTimeField): When the chat room was created.
        updated_at (DateTimeField): When the chat room was last updated.
    """
    employee = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='employee_chatrooms',
        null=True,
        blank=True
    )
    employer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='employer_chatrooms',
        null=True,
        blank=True
    )
    vacancy = models.ForeignKey(
        Vacancy, 
        on_delete=models.CASCADE, 
        related_name='chatrooms',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        employee_name = self.employee.username if self.employee else "Unknown"
        employer_name = self.employer.username if self.employer else "Unknown"
        return f"Chat between {employee_name} and {employer_name}"

    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    """
    Represents a message in a chat room.
    
    Attributes:
        chatroom (ForeignKey): Reference to the chat room this message belongs to.
        sender (ForeignKey): Reference to the user who sent the message.
        content (TextField): The content of the message.
        created_at (DateTimeField): When the message was sent.
        is_read (BooleanField): Whether the message has been read by the recipient.
    """
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )

    def clean(self):
        """
        Validate the message content.
        
        Raises:
            ValidationError: If the content is empty or contains only whitespace.
        """
        if not self.is_deleted and (not self.content or not self.content.strip()):
            raise ValidationError("Message content cannot be empty or contain only whitespace.")

    @property
    def display_content(self):
        """
        Returns the content to display, showing 'Message deleted' if the message is deleted.
        """
        return "Message deleted" if self.is_deleted else self.content

    def delete_message(self, user):
        """
        Soft delete a message if the user is the sender.
        
        Args:
            user: The user attempting to delete the message.
            
        Raises:
            ValidationError: If the user is not the sender of the message.
        """
        if self.sender != user:
            raise ValidationError("You can only delete your own messages.")
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save to run full validation before saving and update chatroom's updated_at.
        """
        self.full_clean()
        super().save(*args, **kwargs)
        # Update the chatroom's updated_at timestamp
        self.chatroom.save(update_fields=['updated_at'])

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']
