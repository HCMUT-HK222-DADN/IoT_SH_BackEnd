from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json, requests
from django.test import RequestFactory

url = "http://127.0.0.1:8000/api/sensorsAction"
headers = {"Content-Type":"application/json"}



class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        self.channel_layer = get_channel_layer()

        await self.channel_layer.group_add(
            'my_group',
            self.channel_name
        )


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'my_group',
            self.channel_name
        )
        # await post_signal.disconnect(self.handle_post_data_received)    

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            # Process the data here
            messType = data['Type']
            message = {
                'Type': 'UpdateSensor'
            }
            if messType == "RequestUpdateSensor":
                response = requests.get(url)
                if response.status_code == 200:
                    response_json = json.loads(response.text)
                    for ele in response_json:
                        if ele['type'] == 'Hu':
                            message['Humi'] = ele['value']
                        if ele['type'] == 'Te':
                            message['Temp'] = ele['value']
                        if ele['type'] == 'Li':
                            message['Light'] = ele['value']
                        if ele['type'] == 'Mo':
                            message['Motion'] = ele['value']
                    print(message)
                else:
                    print("Something went wrong!! ")
            await self.send(json.dumps(message))
        except ValueError:
            # The message is not valid JSON
            await self.send(text_data = "Echo from host: " + text_data)
    
    async def send_message(self, event):
        message = event['message']
        print(message)
        await self.send(json.dumps(message))
