from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from datetime import datetime

User = get_user_model()


class ChatModelsTestCase(TestCase):
    def setUp(self):
        # Create test users with unique emails
        self.employer = User.objects.create_user(
            username="employer", email="employer@test.com", password="testpass123"
        )
        self.employee = User.objects.create_user(
            username="employee", email="employee@test.com", password="testpass123"
        )

        # Create a chat room
        self.chat_room = ChatRoom.objects.create(
            employer=self.employer, employee=self.employee
        )

        # Create a message
        self.message = Message.objects.create(
            chatroom=self.chat_room,
            sender=self.employer,
            content="Hello, this is a test message",
        )

    def tearDown(self):
        User.objects.all().delete()
        ChatRoom.objects.all().delete()
        Message.objects.all().delete()

    def test_chatroom_creation(self):
        self.assertEqual(
            str(self.chat_room),
            f"ChatRoom {self.chat_room.id} ({self.employer} - {self.employee})",
        )
        self.assertTrue(isinstance(self.chat_room.created_at, datetime))

    def test_message_creation(self):
        self.assertEqual(
            str(self.message), f"Message {self.message.id} from {self.employer}"
        )
        self.assertEqual(self.message.content, "Hello, this is a test message")
        self.assertTrue(isinstance(self.message.timestamp, datetime))

    def test_chatroom_relationships(self):
        self.assertEqual(self.chat_room.employer, self.employer)
        self.assertEqual(self.chat_room.employee, self.employee)
        self.assertEqual(self.chat_room.messages.count(), 1)

    def test_message_relationships(self):
        self.assertEqual(self.message.chatroom, self.chat_room)
        self.assertEqual(self.message.sender, self.employer)


class ChatAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users with unique emails
        self.employer = User.objects.create_user(
            username="employer", email="employer@test.com", password="testpass123"
        )
        self.employee = User.objects.create_user(
            username="employee", email="employee@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="testpass123"
        )

        # Get JWT token for employer
        refresh = RefreshToken.for_user(self.employer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Create a test chat room
        self.chat_room = ChatRoom.objects.create(
            employer=self.employer, employee=self.employee
        )

    def tearDown(self):
        User.objects.all().delete()
        ChatRoom.objects.all().delete()
        Message.objects.all().delete()

    def test_start_chat(self):
        # Create a new employee for this test
        new_employee = User.objects.create_user(
            username="new_employee",
            email="new_employee@test.com",
            password="testpass123",
        )

        url = reverse("start-chat")
        data = {"employer_id": self.employer.id, "employee_id": new_employee.id}

        # Test successful chat creation
        self.client.force_authenticate(user=self.employer)  # Authenticate as employer
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ChatRoom.objects.filter(
                employer=self.employer, employee=new_employee
            ).exists()
        )

        # Test duplicate chat creation (should return existing)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test invalid data
        invalid_data = {"employer_id": self.employer.id}
        response = self.client.post(url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test same user chat
        same_user_data = {
            "employer_id": self.employer.id,
            "employee_id": self.employer.id,
        }
        response = self.client.post(url, same_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test unauthorized access
        self.client.force_authenticate(user=None)  # Remove authentication
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SerializerTestCase(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(
            username="employer", email="employer@test.com", password="testpass123"
        )
        self.employee = User.objects.create_user(
            username="employee", email="employee@test.com", password="testpass123"
        )
        self.chat_room = ChatRoom.objects.create(
            employer=self.employer, employee=self.employee
        )
        self.message = Message.objects.create(
            chatroom=self.chat_room, sender=self.employer, content="Test message"
        )

    def tearDown(self):
        User.objects.all().delete()
        ChatRoom.objects.all().delete()
        Message.objects.all().delete()

    def test_message_serializer(self):
        serializer = MessageSerializer(self.message)
        expected_fields = {"id", "chatroom", "sender", "content", "timestamp"}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
        self.assertEqual(serializer.data["content"], "Test message")
        self.assertEqual(serializer.data["sender"], self.employer.id)
        self.assertEqual(serializer.data["chatroom"], self.chat_room.id)

    def test_chatroom_serializer(self):
        serializer = ChatRoomSerializer(self.chat_room)
        expected_fields = {"id", "employer", "employee", "created_at", "messages"}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
        self.assertEqual(serializer.data["employer"], self.employer.id)
        self.assertEqual(serializer.data["employee"], self.employee.id)
        self.assertEqual(len(serializer.data["messages"]), 1)

    def test_message_serializer_validation(self):
        invalid_data = {
            "chatroom": self.chat_room.id,
            "sender": self.employer.id,
            "content": "",  # Empty content should be invalid
        }
        serializer = MessageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_chatroom_serializer_validation(self):
        invalid_data = {
            "employer": self.employer.id,
            "employee": self.employer.id,  # Same user as employer should be invalid
        }
        serializer = ChatRoomSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("employee", serializer.errors)
