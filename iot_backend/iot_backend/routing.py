from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('ws/my_view/', consumers.MyConsumer.as_asgi()),
]
