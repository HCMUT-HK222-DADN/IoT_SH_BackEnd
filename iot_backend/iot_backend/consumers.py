from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json, requests
from django.test import RequestFactory
import asgiref.sync

URL = "http://192.168.1.13:8000/api/"
# URL = "http://127.0.0.1:8000/api/"
URL_SENSOR = URL + "sensorsAction/"
URL_DEVICES = URL + "devicesAction/"
URL_DEVICE_SCHEDULE = URL + "setDeviceAction/"
URL_SESSION = URL + "addSessionRecord/"
URL_GET_SESSION = URL + "getSessionRec/"
URL_SCHEDULE = URL + "setDeviceAction/"
HEADERS = {"Content-Type":"application/json"}

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
            message = {}

            if messType == "RequestUpdateSensor":
                message['Type'] = "UpdateSensor"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR)
                message['Data'] = self.process_all_sensor_data(response)
            elif messType == "RequestUpdateTempSensor":
                message['Type'] = "UpdateTempSensor"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR + "?name=Temp")
                message['Data'] = self.process_all_sensor_data(response)
            elif messType == "RequestUpdateHumidSensor":
                message['Type'] = "UpdateHumidSensor"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR + "?name=Humid")
                message['Data'] = self.process_all_sensor_data(response)
            elif messType == "RequestUpdateLightSensor":
                message['Type'] = "UpdateLightSensor"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR + "?name=Light")
                message['Data'] = self.process_all_sensor_data(response)
            elif messType == "RequestUpdateMotionSensor":
                message['Type'] = "UpdateMotionSensor"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR + "?name=Motion")
                message['Data'] = self.process_all_sensor_data(response)
            elif messType == "RequestDeviceControl":
                message['Type'] = "DeviceControl"
                device_id = data['Device_id']
                value = data['Value']
                payload = {
                    "value": value
                }
                response = await asgiref.sync.sync_to_async(requests.put)(URL_DEVICES + f"{device_id}/", json=payload, headers=HEADERS)
                message['Data'] = json.loads(response.text)
            elif messType == "RequestScheduleBook":
                message['Type'] = "ScheduleBook"
                payload = data['Data']
                response = await asgiref.sync.sync_to_async(requests.post)(URL_SESSION, json=payload, headers=HEADERS)
                message['Data'] = json.loads(response.text)
            elif messType == "RequestSchedule":
                message['Type'] = "Schedule"
                if len(data) > 1:
                    response = await asgiref.sync.sync_to_async(requests.get)(URL_GET_SESSION + str(data['Id']) + "/")
                else:
                    response = await asgiref.sync.sync_to_async(requests.get)(URL_GET_SESSION)
                message['Data'] = json.loads(response.text)
            elif messType == "RequestDeviceTimerBook":
                message['Type'] = "DeviceTimerBook"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_DEVICE_SCHEDULE + "?device_id=" + str(data['Id']))
                message['Data'] = json.loads(response.text)
            await self.send(json.dumps(message))
        except ValueError:
            # The message is not valid JSON
            await self.send(text_data = "Echo from host: " + text_data)
    
    async def send_message(self, event):
        message = event['message']
        print(message)
        await self.send(json.dumps(message))

    def process_all_sensor_data(self, response):
        message = {}
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if len(response_json) > 1:
                for ele in response_json:
                    if ele['type'] == 'Hu':
                        message['Humi'] = ele['value']
                    if ele['type'] == 'Te':
                        message['Temp'] = ele['value']
                    if ele['type'] == 'Li':
                        message['Light'] = ele['value']
                    if ele['type'] == 'Mo':
                        message['Motion'] = ele['value']
            elif response_json[0]['type'] == 'Hu':
                message['Humi'] = response_json[0]['value']
            elif response_json[0]['type'] == 'Te':
                message['Temp'] = response_json[0]['value']
            elif response_json[0]['type'] == 'Li':
                message['Light'] = response_json[0]['value']
            elif response_json[0]['type'] == 'Mo':
                message['Motion'] = response_json[0]['value']
            print(message)
        else:
            print(response.status_code, ": Something went wrong!! ")
        return message
