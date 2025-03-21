import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message
from django.core.exceptions import ObjectDoesNotExist

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        # Get chatroom_id from URL route
        self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        
        # Verify user has access to this chatroom
        if not await self.can_access_chatroom():
            await self.close()
            return

        self.room_group_name = f'chat_{self.chatroom_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            data = text_data_json.get('data', {})

            if message_type == 'chat.message':
                await self.handle_chat_message(data)
            elif message_type == 'chat.typing':
                await self.handle_typing_status(data)
            elif message_type == 'chat.read':
                await self.handle_read_status(data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def handle_chat_message(self, data):
        content = data.get('content')
        if not content:
            return

        # Save message to database
        message = await self.save_message(content)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender_id': self.user.id,
                    'timestamp': message.created_at.isoformat(),
                }
            }
        )

    async def handle_typing_status(self, data):
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.typing',
                'user_id': self.user.id,
                'is_typing': is_typing
            }
        )

    async def handle_read_status(self, data):
        last_read_message_id = data.get('last_read_message_id')
        if not last_read_message_id:
            return

        await self.mark_messages_as_read(last_read_message_id)
        
        # Send message to room group
        message = {
            'type': 'chat.read',
            'user_id': self.user.id,
            'last_read_message_id': last_read_message_id
        }
        await self.channel_layer.group_send(
            self.room_group_name,
            message
        )

    # Message handlers
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps(event))

    # Database operations
    @database_sync_to_async
    def can_access_chatroom(self):
        try:
            chatroom = ChatRoom.objects.get(id=self.chatroom_id)
            return (self.user == chatroom.employee or 
                    self.user == chatroom.employer)
        except ObjectDoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        chatroom = ChatRoom.objects.get(id=self.chatroom_id)
        message = Message.objects.create(
            chatroom=chatroom,
            sender=self.user,
            content=content,
            created_at=timezone.now()
        )
        return message

    @database_sync_to_async
    def mark_messages_as_read(self, last_read_message_id):
        Message.objects.filter(
            chatroom_id=self.chatroom_id,
            id__lte=last_read_message_id
        ).exclude(
            sender=self.user  # Exclude messages from current user
        ).update(is_read=True)