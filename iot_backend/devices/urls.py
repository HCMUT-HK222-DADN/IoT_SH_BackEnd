from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('sensors', views.SensorViewSet)

urlpatterns = [
    path('', include(router.urls))
]