"""
Chutney URL Configuration

Routen:
- /chutney/ - Legacy Django Views (falls benötigt)
- /api/v1/chutney/ - REST API (in api/urls.py)
"""

from django.urls import path, include

app_name = 'chutney'

urlpatterns = [
    # API URLs werden in config/urls.py eingebunden
    # path('api/', include('chutney.api.urls')),
]