"""
Events API - URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EventLogViewSet

router = DefaultRouter()
router.register(r'events', EventLogViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
