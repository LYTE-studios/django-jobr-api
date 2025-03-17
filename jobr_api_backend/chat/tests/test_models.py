from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import CustomUser, ProfileOption
from chat.models import ChatRoom, Message
from vacancies.models import Vacancy

class ChatRoomModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for chat room tests
        """
        self.employee = CustomUser.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.chatroom = ChatRoom.objects.create(
            employee=self.employee,
            employer=self.employer
        )

    def test_chatroom_creation(self):
        """
        Test creating a chat room with users
        """
        self.assertEqual(self.chatroom.employee, self.employee)
        self.assertEqual(self.chatroom.employer, self.employer)

    def test_chatroom_string_representation(self):
        """
        Test the string representation of a chat room
        """
        expected = f"Chat between {self.employee.username} and {self.employer.username}"
        self.assertEqual(str(self.chatroom), expected)

    def test_chatroom_deletion(self):
        """
        Test that deleting a chatroom deletes associated messages
        """
        Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content="Test message"
        )
        self.assertEqual(Message.objects.count(), 1)
        self.chatroom.delete()
        self.assertEqual(Message.objects.count(), 0)

    def test_get_unread_messages(self):
        """
        Test getting unread messages for a user
        """
        # Create messages
        Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content="Message 1"
        )
        Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employer,
            content="Message 2"
        )

        # Get unread messages for employer
        unread_messages = self.chatroom.messages.filter(
            sender=self.employee,
            is_read=False
        )
        self.assertEqual(unread_messages.count(), 1)

class MessageModelTests(TestCase):
    def setUp(self):
        """
        Set up test data for message tests
        """
        self.employee = CustomUser.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.employer = CustomUser.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.chatroom = ChatRoom.objects.create(
            employee=self.employee,
            employer=self.employer
        )

    def test_message_creation(self):
        """
        Test creating a message
        """
        message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content="Test message"
        )
        self.assertEqual(message.content, "Test message")
        self.assertEqual(message.sender, self.employee)
        self.assertFalse(message.is_read)

    def test_message_string_representation(self):
        """
        Test the string representation of a message
        """
        message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content="Test message"
        )
        expected = f"Message from {self.employee.username} at {message.created_at}"
        self.assertEqual(str(message), expected)

    def test_message_content_validation(self):
        """
        Test message content validation
        """
        with self.assertRaises(ValidationError):
            message = Message(
                chatroom=self.chatroom,
                sender=self.employee,
                content=""
            )
            message.full_clean()

        with self.assertRaises(ValidationError):
            message = Message(
                chatroom=self.chatroom,
                sender=self.employee,
                content="   "
            )
            message.full_clean()

    def test_message_cascade_delete(self):
        """
        Test that messages are deleted when chatroom is deleted
        """
        Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content="Test message"
        )
        self.assertEqual(Message.objects.count(), 1)
        self.chatroom.delete()
        self.assertEqual(Message.objects.count(), 0)

    def test_message_sender_deletion(self):
        """
        Test message behavior when sender is deleted
        """
        message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content="Test message"
        )
        self.employee.delete()
        with self.assertRaises(Message.DoesNotExist):
            message.refresh_from_db()