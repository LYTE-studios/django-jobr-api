from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import CustomUser, ProfileOption
from chat.models import ChatRoom, Message
from vacancies.models import Vacancy

class SendMessageViewTests(APITestCase):
    def setUp(self):
        """
        Set up test data for send message view tests
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
        self.send_message_url = reverse('send-message')
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    def test_send_message_to_existing_chatroom(self):
        """
        Test sending a message to an existing chat room
        """
        data = {
            'recipient_id': self.employer.id,
            'content': 'Test message'
        }
        response = self.client.post(self.send_message_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().content, 'Test message')

    def test_send_message_to_new_user(self):
        """
        Test sending a message to a new user (creates new chat room)
        """
        new_employer = CustomUser.objects.create_user(
            username='new_employer',
            email='new@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        data = {
            'recipient_id': new_employer.id,
            'content': 'Test message'
        }
        response = self.client.post(self.send_message_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChatRoom.objects.count(), 2)
        self.assertEqual(Message.objects.count(), 1)

    def test_send_message_without_required_fields(self):
        """
        Test sending a message without required fields
        """
        response = self.client.post(self.send_message_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetMessagesViewTests(APITestCase):
    def setUp(self):
        """
        Set up test data for get messages view tests
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
            sender=self.employer,
            content="Test message"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    def test_get_messages_by_chatroom_id(self):
        """
        Test getting messages using chatroom_id
        """
        url = reverse('get-messages', kwargs={'chatroom_id': self.chatroom.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Test message')

    def test_get_messages_by_user_id(self):
        """
        Test getting messages using user_id
        """
        url = reverse('get-messages', kwargs={'user_id': self.employer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Test message')

    def test_get_messages_marks_as_read(self):
        """
        Test that getting messages marks them as read
        """
        url = reverse('get-messages', kwargs={'chatroom_id': self.chatroom.id})
        self.assertFalse(Message.objects.first().is_read)
        response = self.client.get(url)
        self.assertTrue(Message.objects.first().is_read)

class GetChatRoomListViewTests(APITestCase):
    def setUp(self):
        """
        Set up test data for chat room list view tests
        """
        self.employee = CustomUser.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.employer1 = CustomUser.objects.create_user(
            username='employer1',
            email='employer1@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.employer2 = CustomUser.objects.create_user(
            username='employer2',
            email='employer2@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        self.chatroom1 = ChatRoom.objects.create(
            employee=self.employee,
            employer=self.employer1
        )
        self.chatroom2 = ChatRoom.objects.create(
            employee=self.employee,
            employer=self.employer2
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)
        self.list_url = reverse('get-chatroom-list')

    def test_get_chatroom_list(self):
        """
        Test getting list of chat rooms
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_chatroom_list_ordering(self):
        """
        Test chat rooms are ordered by latest message
        """
        Message.objects.create(
            chatroom=self.chatroom2,
            sender=self.employee,
            content="Latest message"
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.data[0]['id'], self.chatroom2.id)

    def test_unread_messages_count(self):
        """
        Test unread messages count in chat room list
        """
        Message.objects.create(
            chatroom=self.chatroom1,
            sender=self.employer1,
            content="Unread message 1"
        )
        Message.objects.create(
            chatroom=self.chatroom1,
            sender=self.employer1,
            content="Unread message 2"
        )
        response = self.client.get(self.list_url)
        chatroom1_data = next(room for room in response.data if room['id'] == self.chatroom1.id)
        self.assertEqual(chatroom1_data['unread_messages_count'], 2)