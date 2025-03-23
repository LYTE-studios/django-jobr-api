import json
import asyncio
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.test import TestCase
from chat.routing import websocket_urlpatterns
from accounts.models import CustomUser, ProfileOption
from chat.models import ChatRoom, Message
from chat.middleware import TokenAuthMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from django.urls import re_path

import pytest
from channels.db import database_sync_to_async as db_sync

@pytest.mark.django_db
@pytest.mark.asyncio
class TestChatConsumer:
    @pytest.fixture(autouse=True)
    async def setup(self, db):
        """Set up test data and application"""
        # Clean up any existing data
        await db_sync(CustomUser.objects.all().delete)()
        await db_sync(ChatRoom.objects.all().delete)()
        await db_sync(Message.objects.all().delete)()

        # Create test users with unique usernames
        self.employee = await db_sync(CustomUser.objects.create_user)(
            username=f'employee_{id(self)}@test.com',
            email=f'employee_{id(self)}@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )

        self.employer = await db_sync(CustomUser.objects.create_user)(
            username=f'employer_{id(self)}@test.com',
            email=f'employer_{id(self)}@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )
        
        # Create a chat room
        self.chatroom = await db_sync(ChatRoom.objects.create)(
            employee=self.employee,
            employer=self.employer
        )
        
        # Get auth token for employee
        self.token = str(AccessToken.for_user(self.employee))

        # Set up the application with auth middleware
        self.application = TokenAuthMiddleware(URLRouter(websocket_urlpatterns))

        yield

        # Cleanup after test
        await db_sync(CustomUser.objects.all().delete)()
        await db_sync(ChatRoom.objects.all().delete)()
        await db_sync(Message.objects.all().delete)()

    @pytest.mark.asyncio
    async def test_connect_with_valid_token(self):
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_connect_without_token(self):
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is False

    @pytest.mark.asyncio
    async def test_send_and_receive_message(self):
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send a message
        message_data = {
            'type': 'chat.message',
            'data': {
                'content': 'Hello, World!'
            }
        }
        await communicator.send_json_to(message_data)

        # Receive the response
        response = await communicator.receive_json_from()
        
        assert response['type'] == 'chat.message'
        assert response['message']['content'] == 'Hello, World!'
        assert response['message']['sender_id'] == self.employee.id

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_typing_status(self):
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send typing status
        typing_data = {
            'type': 'chat.typing',
            'data': {
                'is_typing': True
            }
        }
        await communicator.send_json_to(typing_data)

        # Receive the response
        response = await communicator.receive_json_from()
        
        assert response['type'] == 'chat.typing'
        assert response['user_id'] == self.employee.id
        assert response['is_typing'] is True

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_read_status(self):
        # Create a test message
        message = await db_sync(Message.objects.create)(
            chatroom=self.chatroom,
            sender=self.employer,
            content='Test message'
        )

        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send read status
        read_data = {
            'type': 'chat.read',
            'data': {
                'last_read_message_id': message.id
            }
        }
        await communicator.send_json_to(read_data)

        # Receive the response
        response = await communicator.receive_json_from()
        
        assert response['type'] == 'chat.read'
        assert response['user_id'] == self.employee.id
        assert response['last_read_message_id'] == message.id

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_invalid_json_handling(self):
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send invalid JSON
        await communicator.send_to(text_data='invalid json')

        # Receive error response
        response = await communicator.receive_json_from()
        assert response['error'] == 'Invalid JSON format'

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_general_exception_handling(self):
        """Test handling of general exceptions in receive method"""
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send a message that will raise a KeyError
        await communicator.send_json_to({
            'type': 'chat.message',
            'data': None  # This will raise a KeyError when trying to access data.get('content')
        })

        # Receive error response with longer timeout
        response = await communicator.receive_json_from(timeout=5)
        assert 'error' in response
        assert "'NoneType' object has no attribute 'get'" in response['error']

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_read_status_marks_messages(self):
        # Create multiple test messages
        message1 = await db_sync(Message.objects.create)(
            chatroom=self.chatroom,
            sender=self.employer,
            content='Test message 1'
        )
        message2 = await db_sync(Message.objects.create)(
            chatroom=self.chatroom,
            sender=self.employer,
            content='Test message 2'
        )
        message3 = await db_sync(Message.objects.create)(
            chatroom=self.chatroom,
            sender=self.employee,  # Message from the current user
            content='Test message 3'
        )

        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send read status for all messages
        read_data = {
            'type': 'chat.read',
            'data': {
                'last_read_message_id': message3.id
            }
        }
        await communicator.send_json_to(read_data)

        # Receive the response
        response = await communicator.receive_json_from()
        assert response['type'] == 'chat.read'
        assert response['last_read_message_id'] == message3.id

        # Verify messages are marked as read in database
        messages = await db_sync(Message.objects.filter)(
            chatroom=self.chatroom,
            sender=self.employer,
            id__lte=message3.id
        )
        messages = await db_sync(list)(messages)
        
        # Check that employer's messages are marked as read
        for message in messages:
            assert await db_sync(lambda: message.is_read)() is True

        # Check that employee's message is not marked as read
        employee_message = await db_sync(Message.objects.get)(id=message3.id)
        assert await db_sync(lambda: employee_message.is_read)() is False

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_invalid_chatroom_access(self):
        # Create another user who shouldn't have access
        other_user = await db_sync(CustomUser.objects.create_user)(
            username='other@test.com',
            email='other@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )
        await db_sync(other_user.save)()
        other_token = str(AccessToken.for_user(other_user))

        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={other_token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is False

    @pytest.mark.asyncio
    async def test_empty_message_content(self):
        """Test sending message with empty content"""
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send empty message
        message_data = {
            'type': 'chat.message',
            'data': {
                'content': ''
            }
        }
        await communicator.send_json_to(message_data)

        # Should not receive a response for empty content
        with pytest.raises(asyncio.TimeoutError):
            await communicator.receive_json_from()

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_nonexistent_chatroom(self):
        """Test connecting to non-existent chatroom"""
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/99999/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is False

    @pytest.mark.asyncio
    async def test_missing_message_type(self):
        """Test sending message without type"""
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send message without type
        message_data = {
            'data': {
                'content': 'Hello'
            }
        }
        await communicator.send_json_to(message_data)

        # Should not receive a response
        with pytest.raises(asyncio.TimeoutError):
            await communicator.receive_json_from()

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect_without_room_group(self):
        """Test disconnect when room_group_name is not set"""
        communicator = WebsocketCommunicator(
            self.application,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        # Don't connect, just disconnect
        await communicator.disconnect()
        # No exception should be raised