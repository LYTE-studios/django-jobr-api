from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message

class SendMessageViewTest(APITestCase):
    def setUp(self):
        """Set up users and an existing chat room."""
         #Get custom user model
        User = get_user_model()

        # Create users with different roles
        self.employee = User.objects.create_user(
            username='employee_user',
            email='employee@example.com',
            password='password123',
            role='employee'
        )
        self.employer = User.objects.create_user(
            username='employer_user',
            email='employer@example.com',
            password='password123',
            role='employer'
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='password123',
            role='admin'
        )

        #Create a chat room and add users
        self.chatroom = ChatRoom.objects.create()
        self.chatroom.users.add(self.employee, self.employer)

        self.client.force_authenticate(user=self.employee)

    def test_send_message_existing_chatroom(self):
        """Test sending a message in an existing chat room."""
        url = reverse("send-message")
        data = {
            "chat_room_id": self.chatroom.id,
            "content": "Starting a new chat."
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(),1)
        self.assertEqual(Message.objects.first().content, "Starting a new chat.")

    def test_send_message_creates_new_chatroom(self):
        """Test creating a new chatroom and sending a message."""
        url = reverse("send-message")
        data = {
            "user_id": self.employer.id,
            "content": "Starting a new chat."
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChatRoom.objects.count(),1)
        self.assertEqual(Message.objects.count(),1)
        self.assertEqual(Message.objects.first().content, "Starting a new chat.")

    def test_send_message_miising_content(self):
        """Test error handling when content is missing"""
        url = reverse("send-message")
        data = {"chat_room_id": self.chatroom.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
    
    def test_send_message_missing_chatroom_and_user_id(self):
        """Test error handling when both chatroom_id and user_id are missing."""
        url = reverse("send-message")
        data = {"content": "Starting a new chat."}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)