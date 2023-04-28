from django.urls import path, include
from . import views
from .views import CreateSensorDataView, DevicesAcionView, SensorActionView, MyView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('sensors', views.SensorsViewSet)
router.register('devices', views.DevicesViewSet) 
router.register('deviceauto', views.DeviceAutoViewSet)
router.register('sensordata', views.SensorDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('insertSensorData/', CreateSensorDataView.as_view(), name='insertSensorData'),
    path('updateDevicesView/<int:pk>/', DevicesAcionView.as_view()),
    path('devicesAction/', DevicesAcionView.as_view()),
    path('devicesAction/<int:pk>/', DevicesAcionView.as_view()),
    path('sensorsAction/', SensorActionView.as_view()),
    path('sensorsAction/<int:pk>/', SensorActionView.as_view()),
#     path('mymodel/', MyView.as_view(), name='my_model_list'),
#     path('mymodel/<int:pk>/', MyView.as_view(), name='my_model_detail'),
]