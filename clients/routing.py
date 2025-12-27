"""
WebSocket URL routing for clients app
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/clients/$', consumers.ClientUpdateConsumer.as_asgi()),
    re_path(r'ws/clients/(?P<client_slug>[\w-]+)/$', consumers.ClientDetailConsumer.as_asgi()),
    # Dashboard uses same consumer for now
    re_path(r'ws/dashboard/$', consumers.ClientUpdateConsumer.as_asgi()),
]