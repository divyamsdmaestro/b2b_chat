from channels.generic.websocket import AsyncJsonWebsocketConsumer


class PingConsumer(AsyncJsonWebsocketConsumer):
    """Just for testing purposes. Ping-Pong Consumer."""

    async def connect(self):
        await self.accept()

    async def receive_json(self, payload, **kwargs):
        if payload["command"] == "PING":
            await self.send_json({"command": "pong", "message": "PONG"})
        else:
            await self.close(400)
