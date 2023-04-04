from rest_framework.serializers import ModelSerializer, ChoiceField
from devices.models import *

class SensorsSerializer(ModelSerializer):
    type = ChoiceField(choices=Sensors.TYPE_CHOICES)
    class Meta:
        model = Sensors
        fields = '__all__'

class DevicesSerializer(ModelSerializer):
    type = ChoiceField(choices=Devices.TYPE_CHOICES)
    class Meta:
        model = Devices
        fields = '__all__'

class DeviceAutoSerializer(ModelSerializer):
    device = DevicesSerializer()
    class Meta:
        model = DeviceAuto
        fields = ['device','value','time_stamp']

class SensorDataSerializer(ModelSerializer):
    # sensor = SensorsSerializer()
    class Meta:
        model = SensorData
        fields = '__all__'

class CreateSensorDataSerializer(ModelSerializer):
    class Meta:
        model = SensorData
        fields = '__all__'

class ChoiceField(ChoiceField):
    def to_representation(self, obj):
        if obj == '' and self.allow_null:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid choice', input=data)