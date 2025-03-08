from .consumer import ChatroomConsumer
from django.urls import path

websocket_urlpatterns = [
    path("/ws/chatroom/<str:chatroom_name>/", ChatroomConsumer.as_asgi()),
]
