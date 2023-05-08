from channels.generic.websocket import AsyncWebsocketConsumer
import json

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass    

    async def receive(self, text_data):
        try:
            # Load json file
            data = json.loads(text_data)
            messType = data['Type']
            # Process the data in case of the messType
            if messType == "RequestUpdateSensor":
                message = {
                    'Type': "UpdateSenor",
                    'Temp': 20,
                    'Humi': 20,
                    'Light': 20,
                    'Motion': 1,
                }
                await self.send(json.dumps(message))
            else:
                print("Cannot read incomming JSON")
        except ValueError:
            # The message is not valid JSON
            print("Error")