"""
SimpleX SMP Monitor - Music Player API URLs
============================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

REST API URL routing for music player.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TrackViewSet,
    PlaylistViewSet,
    CacheStatusView,
    CacheControlView,
    CacheSettingsView,
    LatencyCorrelationView,
)
from .views_cache_forensics import (
    CacheHistoryView,
    CacheAnalyticsView,
    CacheCleanupHistoryView,
)
from .proxy_views import proxy_audio_stream

router = DefaultRouter()
router.register(r'tracks', TrackViewSet, basename='track')
router.register(r'playlists', PlaylistViewSet, basename='playlist')

urlpatterns = [
    # ViewSets
    path('', include(router.urls)),
    
    # Audio Proxy for YouTube streams (CORS bypass)
    path('tracks/<str:track_id>/proxy/', proxy_audio_stream, name='proxy-audio-stream'),
    
    # Cache endpoints
    path('cache/status/', CacheStatusView.as_view(), name='cache-status'),
    path('cache/control/', CacheControlView.as_view(), name='cache-control'),
    path('cache/settings/', CacheSettingsView.as_view(), name='cache-settings'),
    
    # Cache Forensics endpoints
    path('cache/history/', CacheHistoryView.as_view(), name='cache-history'),
    path('cache/history/cleanup/', CacheCleanupHistoryView.as_view(), name='cache-history-cleanup'),
    path('cache/analytics/', CacheAnalyticsView.as_view(), name='cache-analytics'),
    
    # Latency correlation
    path('cache/correlation/', LatencyCorrelationView.as_view(), name='latency-correlation'),
]