import pytest
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import serializers
from chat.serializers import (
    MessageSerializer, ChatRoomSerializer, SendMessageSerializer,
    DeleteMessageSerializer
)
from chat.models import Message, ChatRoom
from accounts.models import CustomUser, ProfileOption
from django.utils import timezone

class TestMessageSerializer(TestCase):
    def setUp(self):
        self.employee = CustomUser.objects.create_user(
            username='employee@test.com',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.employer = CustomUser.objects.create_user(
            username='employer@test.com',
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
            content='Test message'
        )
        self.factory = APIRequestFactory()

    def test_message_serializer_without_request_context(self):
        """Test MessageSerializer without request context"""
        serializer = MessageSerializer(self.message)
        data = serializer.data
        assert data['is_sent_by_me'] is False

    def test_message_serializer_with_request_context(self):
        """Test MessageSerializer with request context"""
        request = self.factory.get('/')
        request.user = self.employee
        serializer = MessageSerializer(self.message, context={'request': request})
        data = serializer.data
        assert data['is_sent_by_me'] is True

    def test_message_content_validation(self):
        """Test content validation for empty messages"""
        request = self.factory.get('/')
        request.user = self.employee
        
        # Test empty content
        serializer = SendMessageSerializer(data={'content': ''})
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
        assert 'This field may not be blank.' in str(serializer.errors['content'][0])

        # Test whitespace content
        serializer = SendMessageSerializer(data={'content': '   '})
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
        assert 'This field may not be blank.' in str(serializer.errors['content'][0])

        # Test direct validate_content method
        serializer = SendMessageSerializer()
        with pytest.raises(serializers.ValidationError) as exc:
            serializer.validate_content('')
        assert 'This field may not be blank.' in str(exc.value)

        with pytest.raises(serializers.ValidationError) as exc:
            serializer.validate_content('   ')
        assert 'This field may not be blank.' in str(exc.value)

    def test_chatroom_unread_messages_count(self):
        """Test unread messages count calculation"""
        # Create messages
        Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employer,
            content='Test message 1'
        )
        Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employer,
            content='Test message 2'
        )
        Message.objects.create(
            chatroom=self.chatroom,
            sender=self.employee,
            content='Test message 3'
        )

        # Test count for employee
        request = self.factory.get('/')
        request.user = self.employee
        serializer = ChatRoomSerializer(self.chatroom, context={'request': request})
        assert serializer.data['unread_messages_count'] == 2

        # Test count without request context
        serializer = ChatRoomSerializer(self.chatroom)
        assert serializer.data['unread_messages_count'] == 0

class TestSendMessageSerializer(TestCase):
    def setUp(self):
        self.employee = CustomUser.objects.create_user(
            username='employee@test.com',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.employer = CustomUser.objects.create_user(
            username='employer@test.com',
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
            content='Test message'
        )
        self.factory = APIRequestFactory()

    def test_send_message_without_context(self):
        """Test SendMessageSerializer without required context"""
        serializer = SendMessageSerializer(data={'content': 'Test message'})
        assert serializer.is_valid()  # Content validation should pass
        with pytest.raises(serializers.ValidationError) as exc:
            serializer.save()  # Should fail due to missing context
        assert 'Missing request or chatroom context' in str(exc.value)

    def test_send_message_with_invalid_reply(self):
        """Test SendMessageSerializer with invalid reply_to"""
        request = self.factory.get('/')
        request.user = self.employee
        serializer = SendMessageSerializer(
            data={'content': 'Test reply', 'reply_to': 99999},
            context={'request': request, 'chatroom': self.chatroom}
        )
        assert not serializer.is_valid()
        assert 'reply_to' in serializer.errors

class TestDeleteMessageSerializer(TestCase):
    def setUp(self):
        self.employee = CustomUser.objects.create_user(
            username='employee@test.com',
            email='employee@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        self.employer = CustomUser.objects.create_user(
            username='employer@test.com',
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
            content='Test message'
        )
        self.factory = APIRequestFactory()

    def test_delete_nonexistent_message(self):
        """Test DeleteMessageSerializer with non-existent message"""
        request = self.factory.get('/')
        request.user = self.employee
        serializer = DeleteMessageSerializer(
            instance=None,
            context={'request': request}
        )
        with pytest.raises(serializers.ValidationError) as exc:
            serializer.validate({})
        assert 'Message not found' in str(exc.value)

    def test_delete_unauthorized_message(self):
        """Test DeleteMessageSerializer with unauthorized user"""
        request = self.factory.get('/')
        request.user = self.employer  # Not the message sender
        serializer = DeleteMessageSerializer(
            instance=self.message,
            context={'request': request}
        )
        with pytest.raises(serializers.ValidationError) as exc:
            serializer.validate({})
        assert 'You can only delete your own messages' in str(exc.value)