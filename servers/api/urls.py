"""
Servers API - URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ServerViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'servers', ServerViewSet, basename='server')

urlpatterns = [
    path('', include(router.urls)),
]
