from channels.generic.websocket import AsyncWebsocketConsumer
import json

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass    

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            # Process the data here
            messageContend = data['message']
            message = {
                'message': "Echo from host: " + messageContend
            }
            await self.send(json.dumps(message))
        except ValueError:
            # The message is not valid JSON
            await self.send(text_data = "Echo from host: " + text_data)

    


