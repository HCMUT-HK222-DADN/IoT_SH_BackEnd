from rest_framework.serializers import ModelSerializer
from devices.models import *

class SensorSerializer(ModelSerializer):
    class Meta:
        model = Sensors
        fields = ['id','name','type','active','value','room','created_date','updated_date']

class DevicesSerializer(ModelSerializer):
    class Meta:
        model = Devices
        fields = ['id','name','type','active','value','room','created_date','updated_date']

class CameraSerializer(ModelSerializer):
    class Meta:
        model = Camera
        fields = ['id','status','room','url']

