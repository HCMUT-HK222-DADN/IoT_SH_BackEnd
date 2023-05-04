from django.urls import path, include
from . import views
from .views import *
# from .views import CreateSensorDataView, DevicesAcionView, SensorActionView, UserRegistrationView, UserLoginView, ChangePasswordView, UserLogoutView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('insertSensorData/', CreateSensorDataView.as_view(), name='insertSensorData'),
    path('updateDevicesView/<int:pk>/', DevicesActionView.as_view()),
    path('devicesAction/', DevicesActionView.as_view()),
    path('devicesAction/<int:pk>/', DevicesActionView.as_view()),
    path('sensorsAction/', SensorActionView.as_view()),
    path('sensorsAction/<int:pk>/', SensorActionView.as_view()),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('logout/all/', BlacklistTokenView.as_view(), name='logout_all'),
    path('changePassword/', ChangePasswordView.as_view(), name='update-password'),
    path('addSessionRecord/', SessionRecordView.as_view(), name='add_session'),
    path('getSessionRec/<int:pk>/', SessionRecordView.as_view(), name='get_session'),
    path('getSessionRec/', SessionRecordView.as_view(), name='get_session'),
    path('updateSessionRec/<int:pk>/', UpdateSessionRecordView.as_view(), name='update_session'),
    path('setDeviceAction/', SetDeviceView.as_view(), name='set_device'),
    path('setDeviceAction/<int:pk>/', SetDeviceView.as_view(), name='get_set_device_specific'),
    path('deleteDeviceAction/<int:my_field_value>/', DeleteSetDevice.as_view(), name='delete_device_by_id'),
    path('deleteSession/<int:my_field_value>/', DeleteSetSession.as_view(), name='delete_session_by_userid'),
    path('checkSetDeviceTimeVsCurrentTime/', CheckDeviceSchedAvailableToEnable.as_view(), name='check_time_stamp_in_set_device'),
    path('getDeviceSuggest/', DeviceAutoSuggest.as_view(), name='get_device_auto'),
    path('getDeviceSuggest/<int:pk>/', DeviceAutoSuggest.as_view(), name='get_device_auto_by_pk'),
    path('addDeviceAuto/', DeviceAutoView.as_view(), name='add_device_auto'),
    path('controlDeviceFromGateway/', ControlDeviceFromMQTT.as_view(), name='control_device_from_gateway'),
    path('deviceUsageHist/', DeviceHstAction.as_view(), name='get_device_usage'),
    path('deviceUsageHist/<int:pk>/', DeviceHstAction.as_view(), name='get_device_usage_by_pk'),

]