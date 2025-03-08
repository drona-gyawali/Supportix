import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatGroup, GroupMessage
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404

User = get_user_model()


class ChatroomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        print(f"User connecting: {self.user}")  # Debugging line

        if not self.user.is_authenticated:
            print("Authentication failed: Rejecting WebSocket")
            await self.close(code=403)  # Reject if user is not authenticated
            return

        self.chatroom_name = self.scope["url_route"]["kwargs"]["chatroom_name"]
        self.chatroom = await sync_to_async(get_object_or_404, thread_sensitive=True)(
            ChatGroup, group_name=self.chatroom_name
        )

        await self.channel_layer.group_add(self.chatroom_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json["body"]

        # Create message asynchronously
        message = await sync_to_async(GroupMessage.objects.create)(
            body=body, author=self.user, group=self.chatroom
        )

        context = {
            "message": message.body,  # Sending only the body instead of the whole object
            "user": self.user.username,  # Convert user object to string
        }

        # Send response in JSON format
        await self.send(text_data=json.dumps(context))

    async def disconnect(self, close_code):
        # Remove user from the chat group on disconnect
        await self.channel_layer.group_discard(self.chatroom_name, self.channel_name)
        print(f"User {self.user.username} has disconnected from {self.chatroom_name}.")
