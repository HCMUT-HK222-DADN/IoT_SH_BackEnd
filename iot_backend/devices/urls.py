from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('sensors', views.SensorViewSet)
router.register('devices', views.DevicesViewSet)
router.register('camera', views.CameraViewSet)

urlpatterns = [
    path('', include(router.urls))
]