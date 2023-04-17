from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json, requests
from django.test import RequestFactory

url = "http://127.0.0.1:8000/api/sensorsAction"
headers = {"Content-Type":"application/json"}



class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_layer = get_channel_layer()

        await self.channel_layer.group_add(
            'my-group',
            self.channel_name
        )

        view_url = "http://127.0.0.1:8000/api/insertSensorData/"

        request = RequestFactory().get(view_url)

        request.channel_layer = self.channel_layer


        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'my-group',
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
                        print(type(ele))
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
    
    # @receiver(post_signal)
    # async def handle_post_signal(sender, **kwargs):
    #     my_data = kwargs.get('data')
    #     print(my_data)
    #     # process my_data and prepare a message to send to the client
    #     message = 'New data: {}'.format(my_data)
    #     await MyConsumer.send_updates(message)

    async def handle_post_data_received(self, sender, **kwargs):
        new_data = kwargs['data']
        print(new_data)
        await self.send(new_data)

    
    @staticmethod
    async def send_updates(message):
        await MyConsumer.group_send('my_group', {'Type': 'RequestUpdateSensor', 'message': message})

    async def send_message(self, event):
        message = event['message']
        await self.send(message)

    async def websocket_connect(self, event):
        await self.channel_layer.group_add('my_group', self.channel_name)
        await self.accept()

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard('my_group', self.channel_name)
