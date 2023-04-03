from django.urls import path, include
from . import views
from .views import CreateSensorDataView, DevicesUpdateView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('sensors', views.SensorsViewSet)
# router.register('devices', views.DevicesViewSet)
router.register('deviceauto', views.DeviceAutoViewSet)
router.register('sensordata', views.SensorDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('insertSensorData/', CreateSensorDataView.as_view(), name='insertSensorData'),
    path('updateDevices/<int:pk>/v', DevicesUpdateView.as_view(), name='update-value')
]