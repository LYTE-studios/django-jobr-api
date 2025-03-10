from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.test import APITestCase, force_authenticate, APIRequestFactory
from django.contrib.auth import get_user_model
from chat.models import Message, ChatRoom
from datetime import datetime

from chat.serializers import MessageSerializer

class MessageSerializerTest(APITestCase):
    def setUp(self):
        #Set up users and chat room
         #Get custom user model
        User = get_user_model()

        # Create users with different roles
        self.sender = User.objects.create_user(
            username='employee_user',
            email='employee@example.com',
            password='password123',
            role='employee'
        )
        self.receiver = User.objects.create_user(
            username='employer_user',
            email='employer@example.com',
            password='password123',
            role='employer'
        )

        #Create a chat room and add users
        self.chatroom = ChatRoom.objects.create()
        self.chatroom.users.add(self.sender, self.receiver)
        self.message = Message.objects.create(chatroom=self.chatroom, sender=self.sender, content="Hello")

    
    def test_message_serializer_valid(self):
        """Test that the MessageSerializer works correctly for a valid message."""
        #Serialize the message
        response = self.client.get("/send-message")
        serializer = MessageSerializer(self.message, context={"request": response.wsgi_request})
        print(self.client.request)

        data = serializer.data
        #Check that the necessary fields are included in the serialized data
        self.assertEqual(set(data.keys()), {"id", "sender", "content", "created_at", "modified_at"
                                            , "read_by", "is_sent_by_me"})
        self.assertEqual(data["content"], "Hello")
        self.assertEqual(data["sender"]["id"], self.sender.id)
        self.assertFalse(data["is_sent_by_me"])

    def test_is_sent_by_me(self):
        """Test the is_send_by_me method of the serializer."""
        self.client.force_authenticate(user=self.sender)
        factory = APIRequestFactory()
        request = self.client.get("/send-message")
        request.user = self.sender
        serializer = MessageSerializer(self.message, context={"request":request})
        data = serializer.data
        self.assertTrue(data["is_sent_by_me"])
        self.client.force_authenticate(user=self.receiver)
        request.user = self.receiver
        serializer = MessageSerializer(self.message, context={"request": request})
        data = serializer.data
        self.assertFalse(data["is_sent_by_me"])

    def test_validate_content_empty(self):
        """Test that an empty content field raises a ValidationError."""
        message_data = {
            "sender": self.sender.id,
            "chatroom": self.chatroom.id,
            "content": "  "
        }
        serializer = MessageSerializer(data=message_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)
        self.assertEqual(serializer.errors["content"][0],"This field may not be blank.")

    def test_serialize_message_with_read_by(self):
        """Test that the read_by field serializes correctly."""
        self.message.read_by.add(self.receiver)
        response = self.client.get("/send-message")
        serializer = MessageSerializer(self.message, context={"request": response.wsgi_request})
        data = serializer.data
        self.assertIn("read_by", data)
        self.assertEqual(len(data["read_by"]), 1)
        self.assertEqual(data["read_by"][0]["id"], self.receiver.id)

    def test_message_serializer_no_sender(self):
        """Test that the serializer raises a validation error if sender is missing."""
        message_data = {
            "chatroom": self.chatroom.id,
            "content": "A message without a sender",
        }
        self.client.force_authenticate(user=self.sender)
        url = reverse("send-message")
        response = self.client.post(url, message_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_message_serializer_with_sender(self):
        """Test serializer works when sender is included."""
        message_data = {
            "chatroom": self.chatroom.id,
            "content": "A message without a sender",
            "sender": self.sender.id,
        }
        serializer = MessageSerializer(data=message_data)
        self.assertTrue(serializer.is_valid())


    