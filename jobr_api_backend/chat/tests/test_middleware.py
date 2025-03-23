import pytest
from datetime import timedelta
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from chat.middleware import TokenAuthMiddleware, get_user_from_token
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from chat.routing import websocket_urlpatterns
from channels.db import database_sync_to_async
from accounts.models import ProfileOption
from chat.models import ChatRoom

User = get_user_model()

@pytest.mark.asyncio
class TestTokenAuthMiddleware:
    @pytest.fixture(autouse=True)
    async def setup(self, db):
        # Clean up any existing data
        await database_sync_to_async(User.objects.all().delete)()
        await database_sync_to_async(ChatRoom.objects.all().delete)()

        # Create test users
        self.employee = await database_sync_to_async(User.objects.create_user)(
            username=f'employee_{id(self)}@test.com',
            email=f'employee_{id(self)}@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYEE
        )

        self.employer = await database_sync_to_async(User.objects.create_user)(
            username=f'employer_{id(self)}@test.com',
            email=f'employer_{id(self)}@test.com',
            password='testpass123',
            role=ProfileOption.EMPLOYER
        )

        # Create a chat room
        self.chatroom = await database_sync_to_async(ChatRoom.objects.create)(
            employee=self.employee,
            employer=self.employer
        )
        
        # Get auth token for employee
        self.token = str(AccessToken.for_user(self.employee))

        yield

        # Cleanup
        await database_sync_to_async(User.objects.all().delete)()
        await database_sync_to_async(ChatRoom.objects.all().delete)()

    @pytest.mark.asyncio
    async def test_valid_token(self):
        """Test middleware with valid token"""
        app = TokenAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            app,
            f'/ws/chat/{self.chatroom.id}/?token={self.token}'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """Test middleware with invalid token"""
        app = TokenAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            app,
            f'/ws/chat/{self.chatroom.id}/?token=invalid_token'
        )
        connected, _ = await communicator.connect()
        assert not connected

    @pytest.mark.asyncio
    async def test_missing_token(self):
        """Test middleware with no token"""
        app = TokenAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            app,
            f'/ws/chat/{self.chatroom.id}/'
        )
        connected, _ = await communicator.connect()
        assert not connected

    @pytest.mark.asyncio
    async def test_expired_token(self):
        """Test middleware with expired token"""
        # Create an expired token
        expired_token = AccessToken.for_user(self.employee)
        expired_token.set_exp(lifetime=timedelta(days=-1))  # Set expiration to past

        app = TokenAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            app,
            f'/ws/chat/{self.chatroom.id}/?token={expired_token}'
        )
        connected, _ = await communicator.connect()
        assert not connected

    @pytest.mark.asyncio
    async def test_malformed_query_string(self):
        """Test middleware with malformed query string"""
        app = TokenAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            app,
            f'/ws/chat/{self.chatroom.id}/?token='  # Empty token value
        )
        connected, _ = await communicator.connect()
        assert not connected

    @pytest.mark.asyncio
    async def test_get_user_from_token_success(self):
        """Test get_user_from_token with valid token"""
        user = await get_user_from_token(self.token)
        assert user.id == self.employee.id
        assert user.username == self.employee.username

    @pytest.mark.asyncio
    async def test_get_user_from_token_invalid(self):
        """Test get_user_from_token with invalid token"""
        user = await get_user_from_token('invalid_token')
        assert isinstance(user, AnonymousUser)

    @pytest.mark.asyncio
    async def test_get_user_from_token_nonexistent_user(self):
        """Test get_user_from_token with token for deleted user"""
        token = self.token
        await database_sync_to_async(self.employee.delete)()
        user = await get_user_from_token(token)
        assert isinstance(user, AnonymousUser)