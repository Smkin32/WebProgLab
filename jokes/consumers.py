
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RatingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("ratings", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("ratings", self.channel_name)

    async def receive(self, text_data):
        pass

    async def rating_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'rating_update',
            'joke_id': event['joke_id'],
            'rating': event['rating']
        }))
