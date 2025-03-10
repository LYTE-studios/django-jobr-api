from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):

    """
    WebSocket consumer for real-time chat functionality.

    This class handles WebSocket connections for users to join and leave specific chat rooms
    in a Django Channels application. It is responsible for broadcasting messages to all users
    in the same room and receiving messages from the WebSocket.

    Methods:
        connect(self):
            Handles the WebSocket connection. Joins the specified chat room.
        
        disconnect(self, close_code):
            Handles the WebSocket disconnection. Leaves the specified chat room.
        
        receive(self, text_data):
            Receives a message from the WebSocket, processes it, and sends it to the room group.
        
        chat_message(self, event):
            Receives a message from the room group and sends it to the WebSocket for delivery.
    """

    async def connect(self):

        """
        Handles WebSocket connection for the user.

        Retrieves the room name from the URL route and adds the user to the appropriate chat room group.
        After joining the group, the WebSocket connection is accepted.

        """
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):

        """
        Handles WebSocket disconnection for the user.

        Removes the user from the chat room group and closes the connection.

        Arguments:
            close_code (int): The code that indicates the reason for the WebSocket disconnection.

        """
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):

        """
        Receives a message from the WebSocket.

        Processes the received message and sends it to the chat room group for broadcasting to other users.

        Arguments:
            text_data (str): The message received from the WebSocket in JSON format.

        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):

        """
        Receives a message from the chat room group.

        Sends the message to the WebSocket so it can be broadcasted to the user.

        Arguments:
            event (dict): The event containing the message to be sent to the WebSocket.

        """
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
