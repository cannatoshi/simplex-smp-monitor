"""
Stresstests API - URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TestViewSet, TestResultViewSet

router = DefaultRouter()
router.register(r'tests', TestViewSet, basename='test')
router.register(r'results', TestResultViewSet, basename='result')

urlpatterns = [
    path('', include(router.urls)),
]
