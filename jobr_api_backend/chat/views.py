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

    """
    View to send a message in a chat room. The view allows authenticated users 
    to send messages either to an existing chat room or to create a new chat room 
    with another user and send a message.

    Authentication:
        Requires JWT authentication.

    Permissions:
        Only authenticated users can send messages.

    Methods:
        POST: Sends a message to a chat room or creates a new chat room if not found.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        """
        Send a message in a chat room.

        Attributes:
            chat_room_id (int): The ID of the chat room where the message will be sent. 
                                          Required if user_id is not provided.
            content (str): The content of the message to be sent. This field is required.
            user_id (int): The ID of the user to create a new chat room with. 
                                      If provided, a new chat room is created between the authenticated user and the user with the given ID.

        Response:
            - 201 Created: If the message is successfully created, it returns the serialized message data.
            - 400 Bad Request: If chat_room_id or user_id and content are missing, it returns an error message.

        Returns:
            Response: The serialized message data upon success, or an error message if any required fields are missing.
        """

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

    """
    View to retrieve messages from a chat room or between two users.

    This view requires the user to be authenticated via JWT authentication. It handles 
    the retrieval of messages from a chat room. The messages can be fetched by specifying 
    either the `chatroom_id` or `user_id`.

    Authentication:
        Requires a valid JWT token for access.

    Permissions:
        Requires the user to be authenticated (`IsAuthenticated`).

    Methods:
        GET: Retrieves all messages in a chat room or between the authenticated user 
        and another user. Marks unread messages as read.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, chatroom_id=None, user_id=None):

        """
        Retrieve all messages for a specified chat room or between two users.

        Args:
            request (Request): The HTTP request object containing the request data.
            chatroom_id (int): The ID of the chat room to fetch messages from.
            user_id (int): The ID of the user to fetch messages from.

        Returns:
            Response: A response object containing the serialized message data.

        Raises:
            Response: If neither `chatroom_id` nor `user_id` is provided, or if a 
            chat room for the specified `user_id` does not exist.
        """

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

    """
    View to retrieve a list of chat rooms for the authenticated user.

    This view requires the user to be authenticated via JWT authentication. It fetches 
    a list of chat rooms for the authenticated user and returns details about each chat 
    room, including the last message, unread message count, and information about the other user in the chat room.

    Authentication:
        Requires a valid JWT token for access.

    Permissions:
        Requires the user to be authenticated (`IsAuthenticated`).

    Methods:
        GET: Retrieves a list of chat rooms for the authenticated user, including details 
        about the last message, unread messages count, and the other user in the chat room.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        """
        Retrieve a list of chat rooms for the authenticated user, including details about 
        the last message, unread messages count, and the other user in each chat room.

        Args:
            request (Request): The HTTP request object containing the request data.

        Returns:
            Response: A response object containing the list of chat rooms and their details.
        """
        
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
