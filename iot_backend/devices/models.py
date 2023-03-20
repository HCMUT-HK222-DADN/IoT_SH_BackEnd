# from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# class User(AbstractUser):
#     avatar = models.ImageField(upload_to='/uploads/%Y/%m')

###################################### Entities ######################################

class Sensors(models.Model):    #devices_sensors
    TYPE_CHOICES = [
        ('Li', 'Light'),
        ('Te', 'Temp'),
        ('Hu', 'Humid'),
        ('Mo', 'Motion'),
    ]
    name = models.CharField(max_length=100, null=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    active = models.BooleanField(null=False, default=True)
    value = models.FloatField(null=True)
    room = models.CharField(max_length=100, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class User(models.Model):   #devices_user
    username = models.CharField(max_length=100, null=False)
    password = models.CharField(max_length=50, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class Devices(models.Model):    #devices_devices
    # key = models.CharField(primary_key=True) Tạo ra 1 trường có khoá chính
    TYPE_CHOICES = [
        ('LCD', 'LCD'),
        ('Fan', 'Fan'),
        ('Sw', 'Switch'),
        ('Ser', 'Servo'),
    ]
    name = models.CharField(max_length=100, null=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    active = models.BooleanField(null=False, default=False)
    value = models.DecimalField(null=True, max_digits=5, decimal_places=3)
    room = models.CharField(max_length=100, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class Camera(models.Model):
    STATUS_CHOICES = [
        (True, 'Online'),
        (False, 'Disconect')
    ]
    status = models.BooleanField(null=False, choices=STATUS_CHOICES, default=False)
    room = models.CharField(max_length=100, null=False)
    url = models.URLField(max_length = 200, null=True)

###################################### Weak entities ######################################

class DeviceAuto(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(null=False, max_digits=5, decimal_places=3)
    time_stamp = models.DateTimeField(auto_now_add=True)

# def validate_time_end(time_end, time_start):
#     if False:
#         raise ValidationError(
#             _('time_end can not lower than time_start'),
#             params={'Time_start': time_start, 'Time_end': time_end},
#         )

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensors, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(null=False, max_digits=5, decimal_places=3)
    time = models.DateTimeField(auto_now_add=True)

# Các time_start, time_end trong các class bên dưới cần phải sửa lại.
# Giải pháp time_start có thể là auto_now_add, time_end có thể là auto_now, time_trigger = time_end - time_start
# Ràng buộc về time_end > time_start cần gọi validator (chưa hiện thực được)

###################### Weak entity of User ######################
class RestReco(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_start = models.DateTimeField(auto_now=True, null=False)
    time_end = models.DateTimeField(auto_now=True, null=False)
    work_inter = models.CharField(max_length=100, null=False)
    rest_inter = models.CharField(max_length=100, null=False)

class SessionHst(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_start = models.DateTimeField(auto_now=True, null=False)
    time_end = models.DateTimeField(auto_now=True, null=False)

class AlarmReco(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_trigger = models.DateTimeField(auto_now=True, null=True) # time_trigger có thể NULL vì lúc khởi đầu chưa biết được giá trị
    time_start = models.DateTimeField(auto_now=True, null=False)
    time_end = models.DateTimeField(auto_now=True, null=False)

class SleepHst(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_start = models.DateTimeField(auto_now=True, null=False)
    time_end = models.DateTimeField(auto_now=True, null=False)

class AlarmHst(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_trigger = models.DateTimeField(auto_now=True, null=True) # time_trigger có thể NULL vì lúc khởi đầu chưa biết được giá trị
    time_start = models.DateTimeField(auto_now=True, null=False)
    time_end = models.DateTimeField(auto_now=True, null=False)

class SleepReco(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_start = models.DateTimeField(auto_now=True, null=False)
    time_end = models.DateTimeField(auto_now=True, null=False)

class CamRecord(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True)
    sensor = models.ForeignKey(Sensors, on_delete=models.SET_NULL, null=True)
    url = models.URLField(max_length = 200, null=False)
    time_stamp = models.DateTimeField(auto_now_add=True, null=False)

class SetDevice(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(null=False, max_digits=5, decimal_places=3)
    time_stamp = models.DateTimeField(auto_now_add=True, null=False)

class PassInput(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    passwordInput = models.CharField(max_length=50, null=False)
    time_stamp = models.DateTimeField(auto_now_add=True, null=False)

class DeviceHst(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(null=False, max_digits=5, decimal_places=3)
    time_stamp = models.DateTimeField(auto_now_add=True, null=False)

###################################### Relation ######################################
# class Password(models.Model):
#     device = models.ForeignKey(Devices, on_delete=models.SET_NULL, null=True)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     passwordContent = models.CharField(max_length=50, null=False)

###################################### Multi Attribute ######################################
class Option(models.Model):
    alarmHst = models.ForeignKey(AlarmHst, on_delete=models.SET_NULL, null=True)
    # aOption