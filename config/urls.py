from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('servers/', include('servers.urls')),
    path('tests/', include('stresstests.urls')),
    path('events/', include('events.urls')),
]
