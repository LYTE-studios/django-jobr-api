from django.urls import path
from .views import SendMessageView, GetMessagesView, GetChatRoomListView

urlpatterns = [
    path('send/', SendMessageView.as_view(), name='send-message'),
    path('messages/<int:chatroom_id>/', GetMessagesView.as_view(), name='get-messages'),
    path('messages/user/<int:user_id>/', GetMessagesView.as_view(), name='get-messages'),
    path('chatrooms/', GetChatRoomListView.as_view(), name='get-chatroom-list'),
]