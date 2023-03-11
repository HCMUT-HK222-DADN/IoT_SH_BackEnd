from django.db import models

class Devices(models.Model):
    name = models.CharField(max_length=100, null=False)
    type = models.CharField(max_length=100, null=False)
    active = models.BooleanField(null=False, default=False)
    room = models.CharField(max_length=100, null=False)
    created_date = models.DateField(auto_now_add=True)

class Sensors(models.Model):
    name = models.CharField(max_length=100, null=False)
    type = models.CharField(max_length=100, null=False)
    room = models.CharField(max_length=100, null=False)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class Sensor_Data(models.Model):
    sensor = models.ForeignKey(Sensors, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(null=False, max_digits=5, decimal_places=3)
    time = models.DateTimeField(auto_now_add=True)
