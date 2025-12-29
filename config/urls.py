from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Legacy HTMX Views
    path('', include('dashboard.urls')),
    path('servers/', include('servers.urls')),
    path('tests/', include('stresstests.urls')),
    path('events/', include('events.urls')),
    path('clients/', include('clients.urls')),
    
    # REST API v1
    path('api/v1/', include('servers.api.urls')),
    path('api/v1/', include('stresstests.api.urls')),
    path('api/v1/', include('events.api.urls')),
    path('api/v1/', include('clients.api.urls')),
    path('api/v1/dashboard/', include('dashboard.api.urls')),
]
