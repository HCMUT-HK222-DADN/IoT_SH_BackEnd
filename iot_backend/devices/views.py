from django.shortcuts import render
from rest_framework import viewsets, permissions
from devices.models import *
from devices.serializers import *

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