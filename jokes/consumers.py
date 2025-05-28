
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Joke

class JokeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'jokes_updates'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        joke_id = text_data_json['joke_id']
        
        if action in ['like', 'dislike']:
            new_rating = await self.update_joke_rating(joke_id, action)
            
            # Send rating update to all connected clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'rating_update',
                    'joke_id': joke_id,
                    'new_rating': new_rating,
                    'action': action
                }
            )

    async def rating_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'rating_update',
            'joke_id': event['joke_id'],
            'new_rating': event['new_rating'],
            'action': event['action']
        }))

    @database_sync_to_async
    def update_joke_rating(self, joke_id, action):
        try:
            joke = Joke.objects.get(id=joke_id)
            if action == 'like':
                joke.rating += 1
            elif action == 'dislike':
                joke.rating -= 1
            joke.save()
            return joke.rating
        except Joke.DoesNotExist:
            return None
