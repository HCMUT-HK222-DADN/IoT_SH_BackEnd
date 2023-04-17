from django.urls import path
from . import consumers, test_fe_home


websocket_urlpatterns = [
    path('ws/my_view/', consumers.MyConsumer.as_asgi()),
    path('ws/test_FE_Home/', test_fe_home.MyConsumer.as_asgi()),

]
