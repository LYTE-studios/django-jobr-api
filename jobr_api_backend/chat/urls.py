from django.urls import path, re_path
from .views import SendMessageView, GetChatRoomListView, GetMessagesView

urlpatterns = [
    path("send-message", SendMessageView.as_view(), name="send-message"),
    path("messages/chatroom/<int:chatroom_id>", GetMessagesView.as_view(), name="get-messages-chatroom"),
    path("messages/user/<int:user_id>", GetMessagesView.as_view(), name="get-messages-user"),
    path("history", GetChatRoomListView.as_view(), name="get-chatrooms-all"),
]