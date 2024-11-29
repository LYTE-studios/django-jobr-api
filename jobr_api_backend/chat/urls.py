from django.urls import path
from .views import StartChatView, SendMessageView, GetMessagesView

urlpatterns = [
    path('start-chat/', StartChatView.as_view(), name='start-chat'),
    path('send-message/', SendMessageView.as_view(), name='send-message'),
    path('<int:chatroom_id>/history/', GetMessagesView.as_view(), name='get-messages'),
]