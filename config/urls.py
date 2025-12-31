"""
SimpleX SMP Monitor - URL Configuration
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
import time

from core.spa import serve_react_spa


def health_check(request):
    """Health check endpoint for Docker"""
    return JsonResponse({"status": "healthy", "timestamp": time.time()})


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('api/health/', health_check, name='health_check'),
    
    # REST API v1
    path('api/v1/', include('servers.api.urls')),
    path('api/v1/', include('stresstests.api.urls')),
    path('api/v1/', include('events.api.urls')),
    path('api/v1/', include('clients.api.urls')),
    path('api/v1/dashboard/', include('dashboard.api.urls')),
    
    # Legacy clients URLs (if needed)
    path('clients/', include('clients.urls')),
    
    # React SPA - catch all other routes
    re_path(r'^.*$', serve_react_spa, name='spa'),
]
