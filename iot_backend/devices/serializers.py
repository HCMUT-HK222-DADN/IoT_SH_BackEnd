from rest_framework.serializers import ModelSerializer
from devices.models import *

class SensorsSerializer(ModelSerializer):
    class Meta:
        model = Sensors
        fields = ['id','name','type','active','value','room','created_date','updated_date']

class DevicesSerializer(ModelSerializer):
    class Meta:
        model = Devices
        fields = ['id','name','type','active','value','room','created_date','updated_date']

class DeviceAutoSerializer(ModelSerializer):
    device = DevicesSerializer()
    class Meta:
        model = DeviceAuto
        fields = ['device','value','time_stamp']

class SensorDataSerializer(ModelSerializer):
    sensor = SensorsSerializer()
    class Meta:
        model = SensorData
        fields = ['sensor','value','time_stamp']