from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import CustomUser, ProfileOption
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from accounts.serializers import UserSerializer
from django.db.models import Q, Max, Count

class SendMessageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat_room_id = request.data.get("chat_room_id")
        content = request.data.get("content")
        user_id = request.data.get("user_id")

        if not user_id:
            if not all([chat_room_id, content]):
                return Response(
                    {"error": "chat_room_id or user_id, and content are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            chat_room = get_object_or_404(ChatRoom, id=chat_room_id)

        else:
            user = get_object_or_404(CustomUser, id=user_id)
            chat_room = ChatRoom.objects.filter(users=self.request.user).filter(users=user).first()

            if not chat_room:
                chat_room = ChatRoom.objects.create()
                chat_room.users.add(self.request.user)
                chat_room.users.add(user)
                chat_room.save()

        message = Message.objects.create(
            chatroom=chat_room,
            sender_id=request.user.id,
            content=content,
        )

        message.read_by.add(request.user)
        message.save()

        serializer = MessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetMessagesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, chatroom_id=None, user_id=None):
        if chatroom_id:
            chat_room = get_object_or_404(ChatRoom, id=chatroom_id)
        elif user_id:
            user = get_object_or_404(CustomUser, id=user_id)
            try:
                chat_room = ChatRoom.objects.filter(users=self.request.user).filter(users=user).first()
            except ChatRoom.DoesNotExist:
                  return Response([])
        else:
            return Response(
                {"error": "Either chatroom_id or user_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        messages = Message.objects.filter(chatroom=chat_room).order_by("created_at")

        unread_messages = chat_room.get_unread_messages(request.user)

        for message in unread_messages:
            message.read_by.add(request.user)
            message.save()

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)


class GetChatRoomListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all chat rooms for a user and order by the latest message
        chat_rooms = (
            ChatRoom.objects.filter(users=request.user)
            .annotate(last_message_time=Max("messages__created_at"))
            .order_by("-last_message_time")
        )

        chat_rooms_data = []
        for chat_room in chat_rooms:
            last_message = chat_room.messages.order_by("-created_at").first()

            unread_messages_count = chat_room.get_unread_messages(request.user).count()

            other_user = chat_room.users.exclude(id=request.user.id).first()

            chat_room_data = {
                "chat_room": ChatRoomSerializer(chat_room).data,
                "last_message": (
                    MessageSerializer(last_message, context={'request': request}).data if last_message else None
                ),
                "unread_messages_count": unread_messages_count,
                "other_user": UserSerializer(other_user).data,
            }
            chat_rooms_data.append(chat_room_data)

        return Response(chat_rooms_data)
