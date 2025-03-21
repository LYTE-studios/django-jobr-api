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

class DeleteMessageViewTests(APITestCase):
    def setUp(self):
        """
        Set up test data for delete message view tests
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
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    def test_delete_own_message(self):
        """
        Test deleting own message
        """
        url = reverse('delete-message', kwargs={'pk': self.message.id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_deleted)
        self.assertEqual(response.data['content'], "Message deleted")

    def test_delete_others_message(self):
        """
        Test attempting to delete someone else's message
        """
        self.client.force_authenticate(user=self.employer)
        url = reverse('delete-message', kwargs={'pk': self.message.id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_deleted)

    def test_delete_nonexistent_message(self):
        """
        Test attempting to delete a nonexistent message
        """
        url = reverse('delete-message', kwargs={'pk': 99999})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ReplyMessageTests(APITestCase):
    def setUp(self):
        """
        Set up test data for reply message tests
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
        self.original_message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employer,
            content="Original message"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.employee)

    def test_reply_to_message(self):
        """
        Test replying to a message
        """
        data = {
            'recipient_id': self.employer.id,
            'content': 'Reply message',
            'reply_to': self.original_message.id
        }
        response = self.client.post(reverse('send-message'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message']['content'], 'Reply message')
        self.assertEqual(response.data['message']['reply_to_message']['content'], 'Original message')

    def test_reply_to_nonexistent_message(self):
        """
        Test replying to a nonexistent message
        """
        data = {
            'recipient_id': self.employer.id,
            'content': 'Reply message',
            'reply_to': 99999
        }
        response = self.client.post(reverse('send-message'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reply_to_message_in_different_chatroom(self):
        """
        Test replying to a message from a different chatroom
        """
        other_chatroom = ChatRoom.objects.create(
            employee=self.employee,
            employer=CustomUser.objects.create_user(
                username='other_employer',
                email='other@test.com',
                password='testpass123',
                role=ProfileOption.EMPLOYER
            )
        )
        other_message = Message.objects.create(
            chatroom=other_chatroom,
            sender=self.employee,
            content="Message in other chatroom"
        )
        data = {
            'recipient_id': self.employer.id,
            'content': 'Reply message',
            'reply_to': other_message.id
        }
        response = self.client.post(reverse('send-message'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)