from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from devices.models import *
from devices.serializers import *
from django.http import Http404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# from umqtt.robust import MQTTClient
from Adafruit_IO import MQTTClient
import json

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
    
class DevicesViewSet(viewsets.ModelViewSet):
    queryset = Devices.objects.all()
    serializer_class = DevicesSerializer

class DeviceAutoViewSet(viewsets.ModelViewSet):
    queryset = DeviceAuto.objects.all()
    serializer_class = DeviceAutoSerializer

class SensorDataViewSet(viewsets.ModelViewSet):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer

class DevicesAcionView(APIView):
    # def get_object(self, pk):
    #     try:
    #         return Devices.objects.get(pk=pk)
    #     except Devices.DoesNotExist:
    #         raise Http404
        
    # def get(self, request, pk):
    #     # device = self.get_object(pk=pk)
    #     device = Devices.objects.get(pk=pk)
    #     serializer = DevicesSerializer(device)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
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

    def put(self, request, pk):
        # device = self.get_object(pk)
        device = Devices.objects.get(pk=pk)
        serializer = DevicesSerializer(device, data=request.data, partial=True)
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
                sensor_json = json.dumps(SensorsSerializer(sensor).data)
                channel_layer = get_channel_layer()
                print("ASYNC_TO_SYNC")
                async_to_sync(channel_layer.group_send)(
                    "my_group",
                    {
                        'type':'send_message',
                        'message': {
                            'Type': "UpdateSensor",
                            'Temp': newValue,
                            'Humi': 20,
                            'Light': 20,
                            'Motion': 1,
                        }
                    }
                )
                # print(sended)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"errors":"Sensor Id not found!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
