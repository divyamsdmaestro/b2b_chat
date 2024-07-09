from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from apps.chat.models import Message, Room
from apps.chat.serializers import MessageSerializer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """Consumer for Chat. Used to connect/disconnect & send/receive messages."""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room = None
        self.room_group_name = None
        self.room_uuid = None
        self.user = None

    @database_sync_to_async
    def get_room_details(self, uuid):
        """Get the room details using UUID."""

        # TODO: check if the user is in group.
        return Room.objects.filter(uuid=uuid).first()

    async def connect(self):
        """Verify and connect the user to the chat room."""

        self.user = self.scope["user"][0]
        if isinstance(self.user, AnonymousUser):
            return await self.close()

        self.room = await self.get_room_details(self.scope["url_route"]["kwargs"]["room_uuid"])
        if not self.room:
            return await self.close()

        self.room_uuid = self.room.uuid
        self.room_group_name = f"chat_{self.room_uuid}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code=None):
        """Leave the room group."""

        if self.room_group_name:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, payload, **kwargs):
        """Receive message from WebSocket."""

        match payload["command"]:
            case "fetch_messages":
                await self.fetch_messages(payload)
            case "new_message":
                await self.new_message(payload)
            case _:
                await self.disconnect()
                await self.close()

    @database_sync_to_async
    def get_last_10_messages(self):
        """Get the last 10 messages for the currently connected room."""

        return Message.objects.filter(room__uuid=self.room_uuid)[:10]

    @database_sync_to_async
    def get_serialized_messages(self, messages, is_many=True):
        """Serialize the messages."""

        context = {"scope_user": self.user}

        if is_many:
            return MessageSerializer(messages, many=True, context=context).data
        else:
            return MessageSerializer(messages, context=context).data

    async def fetch_messages(self, payload):
        """Fetch older messages for the currently connected room."""

        messages = await self.get_last_10_messages()
        content = {
            "command": "fetched_messages",
            "messages": await self.get_serialized_messages(messages),
            "username": self.user.email,
        }
        await self.send_json(content)

    @database_sync_to_async
    def create_chat(self, msg):
        """Save the message sent on socket to db."""

        return Message.objects.create(user=self.user, room=self.room, content=msg)

    async def new_message(self, payload):
        """Handle new message arrival."""

        message = payload["message"]
        message_obj = await self.create_chat(message)
        serialized_message = await self.get_serialized_messages(message_obj, is_many=False)

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": serialized_message}
        )

    async def chat_message(self, event):
        """Receive message from room group."""

        message = event["message"]

        # Send message to WebSocket
        await self.send_json({"command": "new_message", "message": message})
