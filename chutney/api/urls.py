"""
Chutney API URL Configuration

REST API Endpunkte:
- /api/v1/chutney/networks/
- /api/v1/chutney/nodes/
- /api/v1/chutney/captures/
- /api/v1/chutney/events/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TorNetworkViewSet,
    TorNodeViewSet,
    TrafficCaptureViewSet,
    CircuitEventViewSet,
)

router = DefaultRouter()
router.register(r'networks', TorNetworkViewSet, basename='tornetwork')
router.register(r'nodes', TorNodeViewSet, basename='tornode')
router.register(r'captures', TrafficCaptureViewSet, basename='trafficcapture')
router.register(r'events', CircuitEventViewSet, basename='circuitevent')

urlpatterns = [
    path('', include(router.urls)),
]