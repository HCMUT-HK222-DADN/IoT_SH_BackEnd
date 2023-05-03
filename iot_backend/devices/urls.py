from django.urls import path, include
from . import views
from .views import *
# from .views import CreateSensorDataView, DevicesAcionView, SensorActionView, UserRegistrationView, UserLoginView, ChangePasswordView, UserLogoutView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

router = DefaultRouter()
# router.register('sensors', views.SensorsViewSet)
# router.register('devices', views.DevicesViewSet) 
# router.register('deviceauto', views.DeviceAutoViewSet)
# router.register('sensordata', views.SensorDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('insertSensorData/', CreateSensorDataView.as_view(), name='insertSensorData'),
    path('updateDevicesView/<int:pk>/', DevicesAcionView.as_view()),
    path('devicesAction/', DevicesAcionView.as_view()),
    path('devicesAction/<int:pk>/', DevicesAcionView.as_view()),
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

#     path('mymodel/', MyView.as_view(), name='my_model_list'),
#     path('mymodel/<int:pk>/', MyView.as_view(), name='my_model_detail'),
]