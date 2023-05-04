from rest_framework.serializers import ModelSerializer, ChoiceField, Serializer
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from datetime import datetime
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

class DeviceHstSerializer(ModelSerializer):
    class Meta:
        model = DeviceHst
        fields = '__all__'

class SensorDataSerializer(ModelSerializer):
    # sensor = SensorsSerializer()
    class Meta:
        model = SensorData
        fields = '__all__'

class CreateSensorDataSerializer(ModelSerializer):
    class Meta:
        model = SensorData
        fields = '__all__'

class UserSerializer(ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username']
        )        
        validated_data['password'] = make_password(validated_data['password'], 'md5')
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data['password'], 'md5')
        return super(UserSerializer, self).update(instance, validated_data)

class UserLoginSerializer(ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ('username','password')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class SessionRecordSerializer(ModelSerializer):
    time_start = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    time_end = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = SessionRecord
        fields = '__all__'
    
    def validate(self, data):
        time_start = self.instance.time_start if self.instance else data.get('time_start')
        time_end = self.instance.time_end if self.instance else data.get('time_end')
        print("SERIALIZER: ", time_start, time_end)
        # date_time_start = datetime.strptime(time_start, '%Y-%m-%dT%H:%M:%S%z')
        # date_time_start = time_start
        # date_time_end = datetime.strptime(time_end, '%Y-%m-%dT%H:%M:%S%z')
        if time_start > time_end:
            raise serializers.ValidationError("Time_start must be less then time_end!")
        return data

class SetDeviceSerializer(ModelSerializer):
    value = serializers.FloatField()
    time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    device_name = serializers.SerializerMethodField()
    class Meta:
        model = SetDevice
        fields = ['device','device_name','value','time_stamp','user']

    def get_device_name(self, obj):
        return obj.device.name

class UserLoginSerializer(Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            username=data.get('username',''),
            password=data.get('password','')
        )
        if not user:
            raise serializers.ValidationError('Invalid username or password')
        data['user'] = user
        return data

class DeviceAutoSerializer(ModelSerializer):
    device_name = serializers.SerializerMethodField()
    class Meta:
        model = DeviceAuto
        fields = ['device', 'device_name','value','time_stamp','user']

    def get_device_name(self, obj):
        return obj.device.name

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