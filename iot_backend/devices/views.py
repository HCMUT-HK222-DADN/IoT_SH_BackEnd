from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from devices.models import *
from devices.serializers import *
from django.http import Http404

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
    def get_object(self, pk):
        try:
            return Devices.objects.get(pk=pk)
        except Devices.DoesNotExist:
            raise Http404
        
    def get(self, request, pk):
        device = self.get_object(pk=pk)
        serializer = DevicesSerializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get(self, request):
        room = request.query_params.get('room')
        type = request.query_params.get('type')
        active = request.query_params.get('active')
        devices = Devices.objects.all()
        if room:
            devices = devices.filter(room=room)
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

    def put(self, request, pk, *args, **kwargs):
        device = self.get_object(pk)
        serializer = DevicesSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # serializer_class = DevicesSerializer
       
        


class CreateSensorDataView(APIView):

    def post(self, request):
        """payload: 
            {
                'sensor_id': 1,
                'value': 32
            }
        """
        # print(request.data)
        serializer = CreateSensorDataSerializer(data=request.data)
        if serializer.is_valid():
            sensor_id = request.data.get('sensor_id')
            newValue = request.data.get('value')
            if sensor_id is not None:
                try:
                    sensor = Sensors.objects.get(id=sensor_id)
                except Sensors.DoesNotExist:
                    return Response({"errors":"Invalid Sensor ID!"}, status=status.HTTP_400_BAD_REQUEST)
                sensor.value = newValue
                sensor.save()
                serializer.save(sensor=sensor)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"errors":"Sensor Id not found!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)