from django.urls import path, include
from . import views
from .views import CreateSensorDataView, DevicesAcionView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('sensors', views.SensorsViewSet)
router.register('devices', views.DevicesViewSet) 
router.register('deviceauto', views.DeviceAutoViewSet)
router.register('sensordata', views.SensorDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('insertSensorData/', CreateSensorDataView.as_view(), name='insertSensorData'),
    path('updateDevicesView/<int:pk>', DevicesAcionView.as_view()),
    path('deviceAction/', DevicesAcionView.as_view()),
    # path('device/<int:pk>/get', DevicesUpdateView.as_view())
]