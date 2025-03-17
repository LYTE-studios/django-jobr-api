from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Max, F, Count, Prefetch
from .models import Message, ChatRoom
from .serializers import MessageSerializer, ChatRoomSerializer, SendMessageSerializer
from accounts.models import CustomUser, ProfileOption
from django.db.models import Q, Max, F, Count, Prefetch, Case, When, Value, IntegerField

class SendMessageView(generics.CreateAPIView):
    """
    View for sending messages. Creates a new chat room if one doesn't exist.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SendMessageSerializer

    def post(self, request, *args, **kwargs):
        recipient_id = request.data.get('recipient_id')
        vacancy_id = request.data.get('vacancy_id')
        content = request.data.get('content')

        if not recipient_id or not content:
            return Response(
                {"error": "Both recipient_id and content are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            recipient = CustomUser.objects.get(id=recipient_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Recipient not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get or create chat room
        chatroom = ChatRoom.objects.filter(
            (Q(employee=request.user, employer=recipient) |
            Q(employee=recipient, employer=request.user)),
            vacancy_id=vacancy_id
        ).first()

        if not chatroom:
            # Create new chat room
            if request.user.role == ProfileOption.EMPLOYEE:
                chatroom = ChatRoom.objects.create(
                    employee=request.user,
                    employer=recipient,
                    vacancy_id=vacancy_id
                )
            else:
                chatroom = ChatRoom.objects.create(
                    employee=recipient,
                    employer=request.user,
                    vacancy_id=vacancy_id
                )

        # Create and send message
        serializer = self.get_serializer(
            data={'content': content},
            context={'request': request, 'chatroom': chatroom}
        )
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        # Return response with chatroom and message data
        response_data = {
            'message': MessageSerializer(message, context={'request': request}).data,
            'chatroom': ChatRoomSerializer(chatroom, context={'request': request}).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class GetMessagesView(generics.ListAPIView):
    """
    View for retrieving messages from a chat room.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        chatroom_id = self.kwargs.get('chatroom_id')
        user_id = self.kwargs.get('user_id')

        if chatroom_id:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            messages = chatroom.messages.all().order_by('created_at')
        else:
            # Get messages from chat room with specified user
            chatroom = ChatRoom.objects.filter(
                (Q(employee=self.request.user, employer_id=user_id) |
                Q(employee_id=user_id, employer=self.request.user))
            ).first()
            if not chatroom:
                return Message.objects.none()
            messages = chatroom.messages.all().order_by('created_at')

        # Mark messages as read
        messages.filter(
            ~Q(sender=self.request.user),
            is_read=False
        ).update(is_read=True)

        return messages

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        # Add unread messages count for each chat room
        for room_data in data:
            room = ChatRoom.objects.get(id=room_data['id'])
            room_data['unread_messages_count'] = room.messages.filter(
                ~Q(sender=request.user),
                is_read=False
            ).count()
        return Response(data)

class GetChatRoomListView(generics.ListAPIView):
    """
    View for retrieving a list of chat rooms.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        return ChatRoom.objects.filter(
            Q(employee=self.request.user) |
            Q(employer=self.request.user)
        ).prefetch_related(
            Prefetch(
                'messages',
                queryset=Message.objects.order_by('-created_at')
            )
        ).annotate(
            last_message_time=Max('messages__created_at'),
            messages_count=Count('messages'),
            unread_messages_count=Count(
                'messages',
                filter=~Q(messages__sender=self.request.user) & Q(messages__is_read=False)
            )
        ).order_by('-last_message_time')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
