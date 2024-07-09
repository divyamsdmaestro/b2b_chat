from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<uuid:room_uuid>/", consumers.ChatConsumer.as_asgi()),
    path("ws/ping/", consumers.PingConsumer.as_asgi()),
]
