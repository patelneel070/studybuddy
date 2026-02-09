import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.db.models import Q
from .models import ChatMessage
from website.models import StudyBuddyRequest


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user_id = self.scope["user"].id
        self.buddy_id = int(self.scope["url_route"]["kwargs"]["buddy_id"])

        allowed = await self.check_accepted_buddy(self.user_id, self.buddy_id)
        if not allowed:
            await self.close()
            return

        low = min(self.user_id, self.buddy_id)
        high = max(self.user_id, self.buddy_id)
        self.room_group_name = f"chat_{low}_{high}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(" Connected:", self.room_group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        if not message:
            return

        await self.save_message(self.user_id, self.buddy_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))


    @database_sync_to_async
    def check_accepted_buddy(self, user_id, buddy_id):
        return StudyBuddyRequest.objects.filter(
            (
                Q(sender_id=user_id, receiver_id=buddy_id) |
                Q(sender_id=buddy_id, receiver_id=user_id)
            ),
            status="accepted"
        ).exists()

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        ChatMessage.objects.create(
            sender=sender,
            receiver=receiver,
            message=message
        )
