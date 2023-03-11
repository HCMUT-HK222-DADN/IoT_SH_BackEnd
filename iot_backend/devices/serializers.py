from rest_framework.serializers import ModelSerializer
from .models import Sensors

class SensorSerializer(ModelSerializer):
    class Meta:
        model = Sensors
        fields = ['id','name','type','room']