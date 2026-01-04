"""
SimpleX SMP Monitor by cannatoshi
GitHub: https://github.com/cannatoshi/simplex-smp-monitor
Licensed under AGPL-3.0

API URL Configuration

Include this in your main urls.py:
    path('api/v1/', include('clients.api.urls')),
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SimplexClientViewSet,
    ClientConnectionViewSet,
    TestMessageViewSet,
    TestRunViewSet,
)

router = DefaultRouter()
router.register(r'clients', SimplexClientViewSet, basename='client')
router.register(r'connections', ClientConnectionViewSet, basename='connection')
router.register(r'messages', TestMessageViewSet, basename='message')
router.register(r'test-runs', TestRunViewSet, basename='test-run')

urlpatterns = [
    path('', include(router.urls)),
]