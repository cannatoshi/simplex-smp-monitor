"""
Serve React SPA for all non-API routes
"""
import os
from django.http import HttpResponse
from django.conf import settings


def serve_react_spa(request):
    """Serve the React SPA index.html"""
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'static', 'dist', 'index.html'),
        os.path.join(settings.BASE_DIR, 'staticfiles', 'dist', 'index.html'),
    ]
    
    for index_path in possible_paths:
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse(
        '<h1>Frontend not built</h1><p>Run: cd frontend && npm run build</p>',
        content_type='text/html',
        status=500
    )
