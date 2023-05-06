from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json, requests
from django.test import RequestFactory
import asgiref.sync

URL = "http://192.168.137.38:8000/api/"
# URL = "http://127.0.0.1:8000/api/"
URL_SENSOR = URL + "sensorsAction/"
URL_SENSOR_DATA = URL + "getSensorData/"
URL_DEVICES = URL + "devicesAction/"
URL_DEVICE_SCHEDULE = URL + "setDeviceAction/"
URL_DEVICE_HST = URL + "deviceUsageHist/"
URL_SESSION = URL + "addSessionRecord/"
URL_GET_SESSION = URL + "getSessionRec/"
URL_SCHEDULE = URL + "setDeviceAction/"
URL_DEL_DEVICE_SCHEDULE = URL + "deleteDeviceAction/"
URL_DEL_SESSION_SCHEDULE = URL + "deleteSession/"
URL_GET_DEVICE_SUGGEST = URL + "getDeviceSuggest/"
URL_LOGIN = URL + "login/"
URL_AUTOCHECK = URL + "checkSetDeviceTimeVsCurrentTime/"
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
        print("\nRECEIVER: ", text_data)
        try:
            data = json.loads(text_data)
            # Process the data here
            messType = data['Type']
            message = {}

            if messType == "RequestUpdateSensor":
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR)
                message = self.process_all_sensor_data(response)
                message['Type'] = "UpdateSensor"
            elif messType == "RequestUpdateTempSensor":
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR + "?name=Temp")
                message['Data'] = self.process_all_sensor_data(response)
                message['Type'] = "UpdateTempSensor"
            elif messType == "RequestUpdateHumiSensor":
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR + "?name=Humid")
                message['Data'] = self.process_all_sensor_data(response)
                message['Type'] = "UpdateHumiSensor"
            elif messType == "RequestUpdateLightSensor":
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR + "?name=Light")
                message['Data'] = self.process_all_sensor_data(response)
                message['Type'] = "UpdateLightSensor"
            elif messType == "RequestUpdateMotionSensor":
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR + "?name=Motion")
                message['Data'] = self.process_all_sensor_data(response)
                message['Type'] = "UpdateMotionSensor"
            elif messType == "RequestDeviceStatus":
                response = await asgiref.sync.sync_to_async(requests.get)(URL_DEVICES)
                message['Type'] = "DeviceInit"
                message['Data'] = []
                res_obj = json.loads(response.text)
                for ele in res_obj:
                    data = {
                        "Device":ele['name'],
                        "Value":ele['value'],
                        "Active":ele['active']
                    }
                    message['Data'].append(data)


            elif messType == "RequestDeviceControl":
                message['Type'] = "DeviceControl"
                device_name = data['Device']
                value = data['Value']
                payload = {
                    "name": device_name,
                    "value": value,
                }
                response = await asgiref.sync.sync_to_async(requests.put)(URL_DEVICES, json=payload, headers=HEADERS)
                message['Data'] = json.loads(response.text)
                

            elif messType == "RequestScheduleBook":
                message['Type'] = "ScheduleBook"
                payload = {
                    "user_id":data['UserID'],
                    "time_start": data['time_start'],
                    "time_end": data['time_end'],
                    "work_inter": data['work_inter'],
                    "rest_inter": data['rest_inter']
                }
                response = await asgiref.sync.sync_to_async(requests.post)(URL_SESSION, json=payload, headers=HEADERS)
                message['Data'] = json.loads(response.text)
            elif messType == "RequestSchedule":
                message['Type'] = "Schedule"
                payload = {
                    "user_id": data['UserID']
                }
                response = await asgiref.sync.sync_to_async(requests.get)(URL_GET_SESSION, json=payload)
                message['Data'] = json.loads(response.text)
            elif messType == "RequestDeviceTimerBook":
                message['Type'] = "DeviceTimerBook"
                payload = {
                    "device_name": data["Device"],
                    "user_id": data["UserID"],
                    "value": data["Value"],
                    "time_stamp": data["TimeStart"]
                }
                response = await asgiref.sync.sync_to_async(requests.post)(URL_DEVICE_SCHEDULE, json=payload)
                message['Data'] = json.loads(response.text)
            elif messType == "RequestDeviceTimerSchedule":
                message['Type'] = "DeviceTimerSchedule"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_DEVICE_SCHEDULE + "?user_id=" + str(data['UserID']))
                res_obj = json.loads(response.text)
                message['Data'] = []
                for ele in res_obj:
                    data = {
                        "Device": ele['device_name'],
                        "Value": ele['value'],
                        "TimeStart": ele['time_stamp']
                    }
                    message['Data'].append(data)
            elif messType == "RequestDeviceTimerDelete":
                message['Type'] = "DeviceTimerDelete"
                payload = {
                    "position": data['Position']
                }
                response = await asgiref.sync.sync_to_async(requests.delete)(URL_DEL_DEVICE_SCHEDULE + str(data['UserID']) + "/", json=payload)
            elif messType == "RequestScheduleDelete":
                message['Type'] = "ScheduleDelete"
                payload = {
                    "position": data['Position']
                }
                response = await asgiref.sync.sync_to_async(requests.delete)(URL_DEL_SESSION_SCHEDULE + str(data['UserID']) + "/", json=payload)
            elif messType == "RequestDeviceTimerSuggest":
                message['Type'] = 'DeviceTimerSuggest'
                URL_PREP = URL_GET_DEVICE_SUGGEST + "?UserID=" + str(data['UserID']) + "&Device=" + data['Device'] + "&Value=" + str(data["Value"])
                response = await asgiref.sync.sync_to_async(requests.get)(URL_PREP)
                res_obj = json.loads(response.text)
                for i in range(0,len(res_obj)):
                    message["time" + str(i + 1)] = res_obj[i]['time_stamp']
            elif messType == "RequestLogIn":
                message['Type'] = 'LogIn'
                payload = {
                    'username':data['Username'],
                    'password':data['Password']
                }
                response = await asgiref.sync.sync_to_async(requests.post)(URL_LOGIN, json=payload)
                message['UserID'] = int(response.text)
            elif messType == "RequestSensorData":
                message['Type'] = "SensorData"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_SENSOR_DATA + "?Sensor=" + str(data['Sensor']))
                message['Data'] = json.loads(response.text)
            elif messType == "RequestAddDeviceHistory":
                message['Type'] = "AddDeviceHistory"
                payload = {
                    "UserID": data['UserID'],
                    "Device": data['Device'],
                    "value": data['Value'],
                    "time_stamp": data['TimeStamp']
                }
                response = await asgiref.sync.sync_to_async(requests.post)(URL_DEVICE_HST, json=payload)
            elif messType == "RequestAutoCheckTimeStartInSetDevice":
                message['Type'] = "AutoCheckTimeStartInSetDevice"
                response = await asgiref.sync.sync_to_async(requests.get)(URL_AUTOCHECK)


            await self.send(json.dumps(message))
        except ValueError:
            # The message is not valid JSON
            await self.send(text_data = "Echo from host: " + text_data)
    
    async def send_message(self, event):
        message = event['message']
        print(message)
        await self.send(json.dumps(message))
    
    async def send_request(self, event):
        message = event['message']
        print(message)
        await self.receive

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
