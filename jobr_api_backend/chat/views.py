from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

class StartChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employer_id = request.data.get('employer_id')  # Fixed: was employee_id
        employee_id = request.data.get('employee_id')  # Fixed: was employer_id
        
        if not employer_id or not employee_id:
            return Response(
                {"error": "Both employer_id and employee_id are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if employee_id == employer_id:
            return Response(
                {"error": "Employer and Employee cannot be the same user."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Verify the authenticated user is the employer
        if request.user.id != employer_id:
            return Response(
                {"error": "You can only start chats as yourself"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        chat_room, created = ChatRoom.objects.get_or_create(
            employer_id=employer_id, 
            employee_id=employee_id
        )
        serializer = ChatRoomSerializer(chat_room)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

class SendMessageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat_room_id = request.data.get('chat_room_id')
        sender_id = request.data.get('sender_id')
        content = request.data.get('content')

        if not all([chat_room_id, sender_id, content]):
            return Response(
                {"error": "chat_room_id, sender_id, and content are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        
        # Verify the sender is part of the chat room
        if sender_id not in [chat_room.employer.id, chat_room.employee.id]:
            return Response(
                {'error': 'You are not authorized to send messages in this chat room'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Verify the authenticated user is the sender
        if request.user.id != sender_id:
            return Response(
                {"error": "You can only send messages as yourself"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        message = Message.objects.create(
            chatroom=chat_room, 
            sender_id=sender_id, 
            content=content
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GetMessagesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, chatroom_id=None):
        if chatroom_id:
            chat_room = get_object_or_404(ChatRoom, id=chatroom_id)
            
            # Verify the user is part of the chat room
            if request.user.id not in [chat_room.employer.id, chat_room.employee.id]:
                return Response(
                    {'error': 'You are not authorized to view messages in this chat room'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            messages = Message.objects.filter(chatroom=chat_room).order_by('timestamp')
        else:
            # Only return messages from chat rooms the user is part of
            messages = Message.objects.filter(
                chatroom__in=ChatRoom.objects.filter(
                    models.Q(employer=request.user) | 
                    models.Q(employee=request.user)
                )
            ).order_by('timestamp')
            
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)