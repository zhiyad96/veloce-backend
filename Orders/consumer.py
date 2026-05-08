from channels.generic.websocket import AsyncWebsocketConsumer
import json


class OrderConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.group_name = "test_user"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        print("WebSocket Connected")


    async def disconnect(self, close_code):

        if hasattr(self, "group_name"):

            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

            print("Disconnected")


    async def send_status(self, event):

        print("EVENT RECEIVED:", event)

        await self.send(text_data=json.dumps({
            "order_id": event["order_id"],
            "status": event["status"]
        }))