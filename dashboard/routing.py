from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    re_path(r'ws/test/(?P<test_id>\d+)/$', consumers.TestConsumer.as_asgi()),
]
