from django.test import TestCase
from rest_framework.test import APIRequestFactory
from accounts.models import CustomUser, ProfileOption
from chat.models import ChatRoom, Message
from chat.serializers import MessageSerializer, ChatRoomSerializer, SendMessageSerializer
from django.utils import timezone

class MessageSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for message serializer tests
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
        self.message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content="Test message"
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.employee

    def test_message_serialization(self):
        """
        Test serializing a message
        """
        serializer = MessageSerializer(self.message, context={'request': self.request})
        data = serializer.data
        
        self.assertEqual(data['content'], "Test message")
        self.assertEqual(data['sender']['username'], 'employee')
        self.assertFalse(data['is_read'])

    def test_message_validation(self):
        """
        Test message content validation
        """
        serializer = SendMessageSerializer(data={'content': ''}, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

    def test_is_sent_by_me_field(self):
        """
        Test is_sent_by_me field calculation
        """
        serializer = MessageSerializer(self.message, context={'request': self.request})
        self.assertTrue(serializer.data['is_sent_by_me'])
        
        # Test with different user
        self.request.user = self.employer
        serializer = MessageSerializer(self.message, context={'request': self.request})
        self.assertFalse(serializer.data['is_sent_by_me'])

class ChatRoomSerializerTests(TestCase):
    def setUp(self):
        """
        Set up test data for chatroom serializer tests
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
        self.message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content="Test message"
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.employee

    def test_chatroom_serialization(self):
        """
        Test serializing a chatroom
        """
        serializer = ChatRoomSerializer(self.chatroom, context={'request': self.request})
        data = serializer.data
        
        self.assertEqual(data['employee']['username'], 'employee')
        self.assertEqual(data['employer']['username'], 'employer')
        self.assertEqual(len(data['messages']), 1)

    def test_chatroom_nested_message_serialization(self):
        """
        Test nested message serialization in chatroom
        """
        serializer = ChatRoomSerializer(self.chatroom, context={'request': self.request})
        data = serializer.data
        
        message_data = data['messages'][0]
        self.assertEqual(message_data['content'], "Test message")
        self.assertEqual(message_data['sender']['username'], 'employee')
        self.assertTrue(message_data['is_sent_by_me'])

    def test_unread_messages_count(self):
        """
        Test unread messages count calculation
        """
        # Create unread message from employer
        Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employer,
            content="Unread message"
        )
        
        serializer = ChatRoomSerializer(self.chatroom, context={'request': self.request})
        self.assertEqual(serializer.data['unread_messages_count'], 1)

    def test_last_message(self):
        """
        Test last message retrieval
        """
        new_message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employer,
            content="Latest message"
        )
        
        serializer = ChatRoomSerializer(self.chatroom, context={'request': self.request})
        last_message = serializer.data['last_message']
        
        self.assertEqual(last_message['content'], "Latest message")
        self.assertEqual(last_message['sender']['username'], 'employer')