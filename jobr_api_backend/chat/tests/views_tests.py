from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message
from chat.views import GetMessagesView

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


class GetMessagesViewTest(APITestCase):
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
        #Create a chat room and add users
        self.chatroom = ChatRoom.objects.create()
        self.chatroom.users.add(self.employee, self.employer)

        #Create messages in the chatroom
        self.message1 = Message.objects.create(chatroom=self.chatroom, sender=self.employee, content="Hello")
        self.message2 = Message.objects.create(chatroom=self.chatroom, sender=self.employer, content="Hello world")

        self.client.force_authenticate(user=self.employee)

    def test_get_messages_by_chatroom_id(self):
        """Retrive messages using chatroom_id."""
        url = reverse("get-messages-chatroom", kwargs={"chatroom_id": self.chatroom.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["content"], "Hello")
        self.assertEqual(response.data[1]["content"], "Hello world")

    def test_get_messages_by_user_id(self):
        """Retrive messages using user_id."""
        url = reverse("get-messages-user", kwargs={"user_id": self.employer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["content"], "Hello")
        self.assertEqual(response.data[1]["content"], "Hello world")

    def test_unread_messages_marked_as_read(self):
        """Unread messages should be marked as read when retrieved."""
        self.assertEqual(self.message2.read_by.count(),0)
        url = reverse("get-messages-chatroom", kwargs={"chatroom_id": self.chatroom.id})
        response = self.client.get(url)
        self.message2.refresh_from_db()
        self.assertIn(self.employee, self.message2.read_by.all())

    def test_missing_chatroom_id_and_user_id(self):
        """Request without chatroom_id or user_id."""
        view = GetMessagesView.as_view()
        factory = APIRequestFactory()
        request = factory.get("messages/chatroom/")
        force_authenticate(request, user=self.employee)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Either chatroom_id or user_id is required.")


    
