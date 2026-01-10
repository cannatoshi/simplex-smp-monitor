"""
SimpleX SMP Monitor - Music Player Admin
=========================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

Admin interface for music player models.
"""
from django.contrib import admin
from .models import Track, Playlist, PlaylistEntry, AudioCacheLog, CacheSettings


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'source_type', 'duration', 'is_cached', 'play_count', 'created_at']
    list_filter = ['source_type', 'is_cached', 'created_at']
    search_fields = ['title', 'artist', 'source_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'playlist_type', 'track_count', 'is_public', 'created_at']
    list_filter = ['playlist_type', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-updated_at']


@admin.register(PlaylistEntry)
class PlaylistEntryAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'position', 'track', 'added_at']
    list_filter = ['playlist', 'added_at']
    ordering = ['playlist', 'position']


@admin.register(AudioCacheLog)
class AudioCacheLogAdmin(admin.ModelAdmin):
    list_display = [
        'video_id', 
        'status', 
        'file_size_display', 
        'bandwidth_display',
        'started_at', 
        'completed_at'
    ]
    list_filter = ['status', 'started_at', 'audio_format']
    search_fields = ['video_id', 'error_message']
    readonly_fields = [
        'id', 'started_at', 'completed_at',
        'download_started_at', 'download_completed_at',
        'conversion_started_at', 'conversion_completed_at'
    ]
    ordering = ['-started_at']
    
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        if obj.file_size_bytes:
            mb = obj.file_size_bytes / (1024 * 1024)
            return f"{mb:.2f} MB"
        return "-"
    file_size_display.short_description = "File Size"
    
    def bandwidth_display(self, obj):
        """Display bandwidth in human readable format."""
        if obj.bandwidth_bytes_per_sec:
            mbps = (obj.bandwidth_bytes_per_sec * 8) / (1024 * 1024)
            return f"{mbps:.2f} Mbps"
        return "-"
    bandwidth_display.short_description = "Bandwidth"


@admin.register(CacheSettings)
class CacheSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'cache_enabled', 
        'max_cache_size_mb', 
        'max_concurrent_downloads',
        'auto_cleanup_enabled',
        'cleanup_after_days'
    ]
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not CacheSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False