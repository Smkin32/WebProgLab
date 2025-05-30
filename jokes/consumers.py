
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Joke

class YourConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        # Add this connection to a group for rating updates
        await self.channel_layer.group_add("ratings", self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'rate_joke':
                joke_id = data.get('joke_id')
                action = data.get('action')
                
                # Update the joke rating
                new_rating = await self.update_joke_rating(joke_id, action)
                
                if new_rating is not None:
                    # Broadcast the new rating to all connected clients
                    await self.channel_layer.group_send("ratings", {
                        "type": "rating_update",
                        "joke_id": joke_id,
                        "rating": new_rating
                    })
                    
        except json.JSONDecodeError:
            pass

    async def disconnect(self, close_code):
        # Remove from the group
        await self.channel_layer.group_discard("ratings", self.channel_name)

    async def rating_update(self, event):
        # Send rating update to WebSocket
        await self.send(text_data=json.dumps({
            "type": "rating_update",
            "joke_id": event["joke_id"],
            "rating": event["rating"]
        }))

    @database_sync_to_async
    def update_joke_rating(self, joke_id, action):
        try:
            joke = Joke.objects.get(id=joke_id)
            if action == 'up':
                joke.rating += 1
            elif action == 'down':
                joke.rating -= 1
            joke.save()
            return joke.rating
        except Joke.DoesNotExist:
            return None
