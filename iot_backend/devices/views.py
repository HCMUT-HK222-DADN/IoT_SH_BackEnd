from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer 
from rest_framework_simplejwt.views import TokenBlacklistView , TokenViewBase
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth import logout
from devices.models import *
from devices.serializers import *
from django.http import Http404
from channels.layers import get_channel_layer
from devices.models import OutstandingToken
from asgiref.sync import async_to_sync
from django.contrib.auth.hashers import make_password, check_password, MD5PasswordHasher
from Adafruit_IO import MQTTClient
from datetime import datetime, date
import json, schedule, subprocess, time

AIO_USERNAME = "LamVinh"
AIO_KEY = "aio_HUyW98JRfR6disI1VkEDqEZ9f7G0"
AIO_FEED = {
    "Fan" : "fan",
    "Light" : "button1"
}

client = MQTTClient(AIO_USERNAME, AIO_KEY)

class DeviceStatusExe:
    def execute():
        pass

class SensorsViewSet(viewsets.ModelViewSet):
    queryset = Sensors.objects.all()
    serializer_class = SensorsSerializer
    
    # Tạo bảo mật cho phép xem khi đăng nhập
    # permission_classes = [permissions.IsAuthenticated]
    
    # Tạo bảo mật chỉ cho xem mà không thao tác được các thao tác khác
    # def get_permissions(self):
    #     if self.action == 'list':
    #         return [permissions.AllowAny()]
    #     return [permissions.IsAuthenticated()]


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'detail': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):
            return Response({'detail': 'Invalid Password'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user)
        return Response(serializer.data['id'], status=status.HTTP_200_OK)


class UserLogoutView(TokenViewBase):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            jti = token['jti']
            outstanding_token, created = OutstandingToken.objects.get_or_create(jti=jti)
            if not created:
                return Response({'detail': 'Token has already been blacklisted'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'User logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Unable to log out user: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BlacklistTokenView(TokenBlacklistView):
    pass

class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            new_password = serializer.data.get("new_password")
            if not check_password(old_password, self.object.password):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(new_password)
            self.object.save()
            return Response({"status": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DevicesActionView(APIView):
    
    def get(self, request, pk=None):
        if pk is not None:
            sensor = Devices.objects.get(pk=pk)
            serializer = SensorsSerializer(sensor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        id = request.query_params.get('id')
        room = request.query_params.get('room')
        name = request.query_params.get('name')
        type = request.query_params.get('type')
        active = request.query_params.get('active')
        devices = Devices.objects.all()
        if id:
            devices = devices.filter(id=id)
        if room:
            devices = devices.filter(room=room)
        if name:
            devices = devices.filter(name=name)
        if type:
            devices = devices.filter(type=type)
        if active:
            devices = devices.filter(active=active)
        serializer = DevicesSerializer(devices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """payload:
        {
            "name":"Fan1",
            "type":"Fan",
            "active":true,
            "value": 0,
            "room":"Working Room"
        }
        """
        serializer = DevicesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if pk is not None:
            device = self.get_object(pk)
            payload = request.data
        else:
            device = Devices.objects.filter(name=request.data.get('name')).first()
            payload = {
                "value": request.data.get('value')
            }
        serializer = DevicesSerializer(device, data=payload, partial=True)        
        if serializer.is_valid():
            print(serializer)
            serializer.save()
            client.connect()
            if device.type == "Fan":
                client.publish(AIO_FEED['Fan'], request.data.get('value'))
            if device.type == "Sw":
                client.publish(AIO_FEED['Light'], request.data.get('value'))
            client.disconnect()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeviceHstAction(APIView):
    def get(self, request, pk=None):
        if pk is not None:
            devicehst = DeviceHst.objects.get(pk=pk)
            serializer = DeviceHstSerializer(devicehst)
            return Response(serializer.data, status=status.HTTP_200_OK)
        devicehst = DeviceHst.objects.all()
        user_id = request.query_params.get('UserID')
        if user_id:
            devicehst = devicehst.filter(user_id=user_id)
        serializer = DeviceHstSerializer(devicehst, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """
        payload: 
        {
            "time_stamp": "2023-05-04 13:00:00",
            "value":40.0,
            "Device":"Quat",
            "UserID": 1
        }
        """
        user_obj = User.objects.filter(id=request.data.get('UserID')).first()
        if user_obj is None:
            return Response({"error": "User not found!"}, status=status.HTTP_404_NOT_FOUND)
        device_obj = Devices.objects.filter(name=request.data.get('Device')).first()
        if device_obj is None:
            return Response({'error':'Device not found!'}, status=status.HTTP_404_NOT_FOUND)
        data = {
            "value": request.data.get('value'),
            "time_stamp": request.data.get('time_stamp'),
        }
        serializer = DeviceHstSerializer(data=data)
        if serializer.is_valid():
            serializer.save(device=device_obj ,user=user_obj)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ControlDeviceFromMQTT(APIView):
    def put(self, request, pk=None):
        if pk is not None:
            device = Devices.objects.get(pk=pk)
        else:
            device = Devices.objects.filter(name=request.data.get('name')).first()
        data = {
            'value':request.data.get('value')
        }
        serializer = DevicesSerializer(device, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "my_group",
                {
                    'type':'send_message',
                    'message': {
                        "Type":"DeviceControl",
                        "Device": request.data.get('name'),
                        "Value": request.data.get('value')
                        }
                }
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # serializer_class = DevicesSerializer
       
class SensorActionView(APIView):
    def get_object(self, pk):
        try:
            return Sensors.objects.get(pk=pk)
        except Sensors.DoesNotExist:
            raise Http404
        
    def get(self, request, pk = None):
        if pk is not None:
            sensor = self.get_object(pk=pk)
            serializer = SensorsSerializer(sensor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        id = request.query_params.get('id')
        room = request.query_params.get('room')
        name = request.query_params.get('name')
        type = request.query_params.get('type')
        active = request.query_params.get('active')
        sensors = Sensors.objects.all()
        if id:
            sensors = sensors.filter(id=id)
        if room:
            sensors = sensors.filter(room=room)
        if name:
            sensors = sensors.filter(name=name)
        if type:
            sensors = sensors.filter(type=type)
        if active:
            sensors = sensors.filter(active=active)
        serializer = SensorsSerializer(sensors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # def get(self, request, pk):
    #     # sensor = Sensors.objects.get(pk=pk)
    #     sensor = self.get_object(pk=pk)
    #     serializer = SensorsSerializer(sensor)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """payload:
        {
            "type":"Te",
            "name":"T1",
            "active":true,
            "value": 32,
            "room":"Working Room"
        }
        """
        serializer = SensorsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateSensorDataView(APIView):

    def post(self, request):
        """payload: 
            {
                "name": "Light",
                "type": "Li",
                "room": "Working Room",
                "value": payload
            }
        """
        # print(request.data)
        serializer = CreateSensorDataSerializer(data=request.data)
        if serializer.is_valid():
            sensor_name = request.data.get('name')
            sensor_type = request.data.get('type')
            sensor_in_room = request.data.get('room')
            newValue = request.data.get('value')
            if sensor_name is not None:
                try:
                    sensor = Sensors.objects.filter(name=sensor_name, type=sensor_type, room=sensor_in_room).first()
                    # sensor = Sensors.objects.get(id=sensor_id)
                except Sensors.DoesNotExist:
                    return Response({"errors":"Invalid Sensor ID!"}, status=status.HTTP_400_BAD_REQUEST)
                sensor.value = newValue
                sensor.save()
                serializer.save(sensor=sensor)
                message = {
                    'Type':"UpdateSensor"
                }
                if sensor_name == "Light":
                    message['Type'] = "UpdateLightSensor"
                    message['Light'] = newValue
                if sensor_name == "Temp":
                    message['Type'] = "UpdateTempSensor"
                    message['Temp'] = newValue
                if sensor_name == "Humid":
                    message['Type'] = "UpdateHumiSensor"
                    message['Humi'] = newValue
                if sensor_name == "Motion":
                    message['Type'] = "UpdateMotionSensor"
                    message['Motion'] = newValue
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "my_group",
                    {
                        'type':'send_message',
                        'message': message
                    }
                )
                # print(sended)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"errors":"Sensor Id not found!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SessionRecordView(APIView):
    def get(self, request, pk=None):
        try:
            if pk is not None:
                sessionRec = SessionRecord.objects.get(pk=pk)
                serializer = SessionRecordSerializer(sessionRec)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                user_id = request.data.get('user_id')
                sessionRec = SessionRecord.objects.filter(user_id=user_id)
                serializer = SessionRecordSerializer(sessionRec, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except SessionRecord.DoesNotExist:
            return Response({"errors":"Session Record not found!"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        {
            "user_id":1,
            "time_start": "2025-05-25 20:00:00", // 2023-05-02 08:30:00
            "time_end": "1683001800",
            "work_inter": "50",
            "rest_inter": "10"
        }
        """
        user_obj = User.objects.filter(id=request.data.get('user_id')).first()
        if user_obj is None:
            return Response({"errors":"username not found!"}, status=status.HTTP_404_NOT_FOUND)
        datetime_start = datetime.strptime(request.data.get('time_start'), "%Y-%m-%d %H:%M:%S")
        datetime_end = datetime.strptime(request.data.get('time_end'), "%Y-%m-%d %H:%M:%S")
        data = {
            # "time_start": datetime_start,
            # "time_end":datetime_end,
            "time_start": datetime_start,
            "time_end": datetime_end,
            "work_inter": request.data.get('work_inter'),
            "rest_inter": request.data.get('rest_inter')
        }
        serializer = SessionRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateSessionRecordView(APIView):
    def get_object(self, pk):
        try:
            return SessionRecord.objects.get(pk=pk)
        except SessionRecord.DoesNotExist:
            raise Http404
        
    def put(self, request, pk):
        sessionRec = self.get_object(pk)
        print("SESSION START: ", sessionRec.time_start)
        time_end = request.data.get('time_end')
        if time_end:
            request.data['time_end'] = datetime.strptime(time_end, '%Y-%m-%dT%H:%M:%S%z')
        serializer = SessionRecordSerializer(sessionRec, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetDeviceView(APIView):
    def get_object(self, pk):
        try:
            return SetDevice.objects.get(pk=pk)
        except SetDevice.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None):
        if pk is not None:
            device_usage = self.get_object(pk=pk)
            serializer = SetDeviceSerializer(device_usage)
            return Response(serializer.data, status=status.HTTP_200_OK)
        user_id = request.query_params.get('user_id')
        device_name = request.query_params.get('device_name')
        device_scheduled = SetDevice.objects.all()
        if user_id:
            user_obj = User.objects.filter(id=user_id).first()
            device_scheduled = device_scheduled.filter(user=user_obj)
        if device_name:
            device_obj = Devices.objects.filter(name=device_name).first()
            device_scheduled = device_scheduled.filter(device=device_obj)
        serializer = SetDeviceSerializer(device_scheduled, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        {
            "user_id" : 2,
            "device_name" : "Den",
            "value" : 10.1,
            "time_stamp" : "2023-05-02 13:00:00"    
        }
        """
        user_obj = User.objects.filter(id=request.data.get('user_id')).first()
        if user_obj is None:
            return Response({"error": "User not found!"}, status=status.HTTP_404_NOT_FOUND)
        device_obj = Devices.objects.filter(name=request.data.get('device_name')).first()
        if device_obj is None:
            return Response({'error':'Device not found!'}, status=status.HTTP_404_NOT_FOUND)
        data = {
            "value": request.data.get('value'),
            "time_stamp": request.data.get('time_stamp')
        }
        serializer = SetDeviceSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user_obj, device=device_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
class DeleteSetDevice(APIView):
    def delete(self, request, my_field_value):
        try:
            instance_list = SetDevice.objects.filter(user_id=my_field_value)
            pos = request.data.get('position')
            instance = instance_list[pos]
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SetDevice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class DeleteSetSession(APIView):
    def delete(self, request, my_field_value):
        try:
            instance_list = SessionRecord.objects.filter(user_id=my_field_value)
            pos = request.data.get('position')
            instance = instance_list[pos]
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SessionRecord.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class DeviceAutoView(APIView):
    def post(self, request):
        """
        payload = {
            'UserID':1,
            'Device':"Quat",
            'Value': 40.0,
            "Data": ["07:00:00","12:00:00","20:00:00"]
        }
        """
        user_obj = User.objects.filter(id=request.data.get('UserID')).first()
        if user_obj is None:
            return Response({"error": "User not found!"}, status=status.HTTP_404_NOT_FOUND)
        device_obj = Devices.objects.filter(name=request.data.get('Device')).first()
        if device_obj is None:
            return Response({'error':'Device not found!'}, status=status.HTTP_404_NOT_FOUND)
        for data_item in request.data.get('Data'):
            data = {
                'value':request.data.get('Value'),
                'time_stamp':data_item
            }
            serializer = DeviceAutoSerializer(data=data)
            if serializer.is_valid():
                serializer.save(device=device_obj, user=user_obj)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

class DeviceAutoSuggest(APIView):
    def get(self, request, pk=None):
        if pk is not None:
            device_auto = DeviceAuto.objects.get(pk=pk)
            serializer = DeviceAutoSerializer(device_auto)
            return Response(serializer.data, status=status.HTTP_200_OK)
        user_id = request.query_params.get('UserID')
        device_name = request.query_params.get('Device')
        value = request.query_params.get('Value')
        device_obj = Devices.objects.filter(name=device_name).first()
        device_auto = DeviceAuto.objects.filter(user=user_id, device=device_obj, value=value)
        serializer = DeviceAutoSerializer(device_auto, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CheckDeviceSchedAvailableToEnable(APIView):
    def get(self, request):
        print("*******CALL API CHECKING*******")

        schedule.every(30).seconds.do(CheckUtils.check)
        while True:
            schedule.run_pending()
            # setDeviceList = SetDevice.objects.all()
            # if len(setDeviceList) == 0 or setDeviceList is not list:
            #     break
            time.sleep(1)
        return Response('Scheduler start successfully!')

class CheckUtils():
    @staticmethod
    def check():
        print("*******CHECKING*******")
        device_set_list = SetDevice.objects.all().order_by('time_stamp')
        if len(device_set_list) > 0:
            serializer = SetDeviceSerializer(device_set_list[0])
            current_date = datetime.now()
            current_date_obj = datetime.strptime(current_date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            # device_set_date_obj = datetime.strptime(device_set_list[0].time_stamp, "%Y-%m-%d %H:%M:%S")
            print("CURR_DATE: ", current_date_obj)
            device_set_date_obj = device_set_list[0].time_stamp
            print("DEVICE_TIMESTAMP: ", device_set_date_obj)
            check = False
            if current_date_obj.date() == device_set_date_obj.date():
                if current_date_obj.time() >= device_set_date_obj.time():
                    check = True
                    # Call API Update value
            elif current_date_obj.date() > device_set_date_obj.date():
                check = True

            if check:
                message = {
                    "Type":"RequestDeviceControlAuto",
                    "Device": serializer.data['device_name'],
                    "Value": str(serializer.data['value'])
                }
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "my_group",
                    {
                        'type':'send_message',
                        'message': message
                    }
                )
                print("*******DELETING*******\n", json.dumps(message))
                # device_set_list[0].delete()
                    
