"""
SimpleX SMP Monitor - Music Player Serializers
===============================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

REST API serializers for music player.
"""
from rest_framework import serializers
from ..models import Track, Playlist, PlaylistEntry, AudioCacheLog, CacheSettings


class TrackSerializer(serializers.ModelSerializer):
    youtube_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Track
        fields = [
            'id', 'title', 'artist', 'duration',
            'source_type', 'source_id', 'source_url',
            'thumbnail_url', 'youtube_url',
            'play_count', 'is_cached', 'cached_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'play_count', 'is_cached', 'cached_at', 'created_at', 'updated_at']


class TrackCreateFromYouTubeSerializer(serializers.Serializer):
    """Serializer for adding a track from YouTube URL or ID."""
    url_or_id = serializers.CharField(max_length=200, help_text="YouTube URL or Video ID")
    auto_cache = serializers.BooleanField(default=False, help_text="Immediately cache the audio")


class PlaylistEntrySerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    track_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = PlaylistEntry
        fields = ['id', 'track', 'track_id', 'position', 'added_at']
        read_only_fields = ['id', 'added_at']


class PlaylistSerializer(serializers.ModelSerializer):
    track_count = serializers.ReadOnlyField()
    total_duration = serializers.ReadOnlyField()
    entries = PlaylistEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = Playlist
        fields = [
            'id', 'name', 'description', 'thumbnail_url',
            'playlist_type', 'is_public',
            'track_count', 'total_duration', 'entries',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PlaylistListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views (without entries)."""
    track_count = serializers.ReadOnlyField()
    total_duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Playlist
        fields = [
            'id', 'name', 'description', 'thumbnail_url',
            'playlist_type', 'is_public',
            'track_count', 'total_duration',
            'created_at', 'updated_at'
        ]


class AudioCacheLogSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = AudioCacheLog
        fields = [
            'id', 'video_id', 'status', 'is_active',
            'started_at', 'completed_at', 'duration',
            'file_size_bytes', 'download_duration_seconds', 'bandwidth_bytes_per_sec',
            'error_message', 'error_code', 'retry_count',
            'audio_format', 'audio_bitrate'
        ]


class CacheStatusSerializer(serializers.Serializer):
    """Serializer for cache status endpoint."""
    is_caching = serializers.BooleanField()
    active_downloads_count = serializers.IntegerField()
    active_downloads = AudioCacheLogSerializer(many=True)
    recent_failures = AudioCacheLogSerializer(many=True)
    stats = serializers.DictField()


class CacheControlSerializer(serializers.Serializer):
    """Serializer for cache control actions."""
    ACTION_CHOICES = [
        ('cleanup', 'Run cleanup'),
        ('toggle', 'Toggle cache on/off'),
        ('clear_all', 'Clear all cached files'),
        ('cancel_active', 'Cancel active downloads'),
    ]
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    confirm = serializers.BooleanField(default=False, help_text="Required for destructive actions")


class CacheSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CacheSettings
        fields = [
            'cache_enabled', 'max_cache_size_mb',
            'auto_cleanup_enabled', 'cleanup_after_days',
            'max_concurrent_downloads', 'min_delay_between_downloads',
            'preferred_format', 'preferred_bitrate',
            'updated_at'
        ]
        read_only_fields = ['updated_at']