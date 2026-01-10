"""
SimpleX SMP Monitor - Music Player URLs
=======================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

URL routing for music player app.
"""
from django.urls import path, include

app_name = 'music_player'

urlpatterns = [
    path('api/v1/music/', include('music_player.api.urls')),
]