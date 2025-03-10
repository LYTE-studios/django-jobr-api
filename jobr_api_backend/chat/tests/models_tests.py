from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from chat.models import ChatRoom, Message

class ChatRoomModelTest(TestCase):
    def setUp(self):

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

        #Create messages in the chatroom
        self.message1 = Message.objects.create(chatroom=self.chatroom, content="Hello", sender=self.employer)
        self.message2 = Message.objects.create(chatroom=self.chatroom, content="Hello world", sender=self.employee)

        #Mark message1 as read by employer
        self.message1.read_by.add(self.employer)
        

    def test_chatroom_creation(self):
        """Test that the Chatroom instance is created correctly"""
        self.assertEqual(self.chatroom.users.count(), 2)
        self.assertIn(self.employee, self.chatroom.users.all())
        self.assertIn(self.employer, self.chatroom.users.all())

    def test_chatroom_str_method(self):
        """Test the string representation of the Chatroom"""
        expected_str = f"ChatRoom {self.chatroom.id} ({[user.username for user in self.chatroom.users.all()]})"
        self.assertEqual(str(self.chatroom), expected_str)

    
    def test_get_unread_messages_for_employee(self):
        """Test the get_unread_messages method for employee"""
        unread_messages_employee = self.chatroom.get_unread_messages(self.employee)
        unread_messages_employer = self.chatroom.get_unread_messages(self.employer)

        #Assert employee has both messages unread
        self.assertEqual(unread_messages_employee.count(), 2)
        self.assertIn(self.message1, unread_messages_employee)
        self.assertIn(self.message2, unread_messages_employee)

        #Assert employer has a message unread
        self.assertEqual(unread_messages_employer.count(), 1)
        self.assertEqual(unread_messages_employer.first(), self.message2)