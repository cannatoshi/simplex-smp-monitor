"""
Servers API - URL Configuration

Includes Docker hosting endpoints (v0.1.12)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SMPServerViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'servers', SMPServerViewSet, basename='server')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]

# Available endpoints:
# 
# Standard CRUD:
# - GET    /api/v1/servers/              - List all servers
# - POST   /api/v1/servers/              - Create server
# - GET    /api/v1/servers/{id}/         - Get server detail
# - PUT    /api/v1/servers/{id}/         - Update server
# - PATCH  /api/v1/servers/{id}/         - Partial update
# - DELETE /api/v1/servers/{id}/         - Delete server
#
# Docker Actions (NEW):
# - POST   /api/v1/servers/{id}/docker-action/   - Start/Stop/Restart/Delete container
# - GET    /api/v1/servers/{id}/logs/            - Get container logs
# - POST   /api/v1/servers/{id}/sync-status/     - Sync Docker status
# - GET    /api/v1/servers/docker-images/        - Check available images
# - GET    /api/v1/servers/docker-containers/    - List managed containers
# - POST   /api/v1/servers/cleanup-orphaned/     - Remove orphaned containers
#
# Categories:
# - GET    /api/v1/categories/           - List categories
# - POST   /api/v1/categories/           - Create category
# - GET    /api/v1/categories/{id}/      - Get category
# - PUT    /api/v1/categories/{id}/      - Update category
# - DELETE /api/v1/categories/{id}/      - Delete category