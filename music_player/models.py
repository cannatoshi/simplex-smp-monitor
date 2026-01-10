"""
SimpleX SMP Monitor - Music Player Models
==========================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

Audio player models with local caching and latency test correlation.
"""
import uuid
from django.db import models
from django.utils import timezone


class Track(models.Model):
    """Single audio track (YouTube or local file)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    artist = models.CharField(max_length=255, blank=True)
    duration = models.PositiveIntegerField(null=True, help_text="Duration in seconds")
    
    SOURCE_TYPES = [
        ('youtube', 'YouTube'),
        ('local', 'Local File'),
    ]
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='youtube')
    source_id = models.CharField(max_length=100, blank=True, help_text="YouTube Video-ID")
    source_url = models.URLField(max_length=2000, blank=True, help_text="For local files")
    
    thumbnail_url = models.URLField(max_length=2000, blank=True)
    
    # Metadata
    play_count = models.PositiveIntegerField(default=0)
    is_cached = models.BooleanField(default=False)
    cached_at = models.DateTimeField(null=True, blank=True)
    cache_file_path = models.CharField(max_length=500, blank=True, help_text="Path to cached file")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_type', 'source_id']),
            models.Index(fields=['is_cached']),
        ]
    
    def __str__(self):
        return f"{self.artist} - {self.title}" if self.artist else self.title
    
    @property
    def youtube_url(self):
        if self.source_type == 'youtube' and self.source_id:
            return f"https://youtube.com/watch?v={self.source_id}"
        return None


class Playlist(models.Model):
    """Playlist containing multiple tracks"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=2000, blank=True)
    
    PLAYLIST_TYPES = [
        ('user', 'User Playlist'),
        ('curated', 'Curated'),
        ('system', 'System Playlist'),
    ]
    playlist_type = models.CharField(max_length=20, choices=PLAYLIST_TYPES, default='user')
    
    # System playlist identifier (for auto-creation)
    system_key = models.CharField(
        max_length=50, 
        blank=True, 
        unique=True, 
        null=True,
        help_text="Unique key for system playlists (e.g., 'video_help', 'news')"
    )
    
    is_public = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
    
    @property
    def track_count(self):
        return self.entries.count()
    
    @property
    def total_duration(self):
        total = self.entries.aggregate(total=models.Sum('track__duration'))['total']
        return total or 0
    
    @property
    def first_track_thumbnail(self):
        """Get thumbnail from first track for playlist card background."""
        first_entry = self.entries.first()
        if first_entry and first_entry.track.thumbnail_url:
            return first_entry.track.thumbnail_url
        return None
    
    @property
    def is_system_playlist(self):
        """Check if this is a system playlist (cannot be deleted)."""
        return self.playlist_type == 'system'
    
    # =========================================================================
    # System Playlist Definitions
    # =========================================================================
    
    SYSTEM_PLAYLISTS = {
        'video_help': {
            'name': 'Video Help',
            'description': 'Tutorial videos and documentation for SimpleX SMP Monitor',
            'icon': 'video',  # Used by frontend
        },
        'news': {
            'name': 'News',
            'description': 'Latest news and updates about SimpleX and privacy technology',
            'icon': 'news',  # Used by frontend
        },
    }
    
    @classmethod
    def ensure_system_playlists(cls):
        """
        Ensure all system playlists exist in the database.
        Called on app startup or first API request.
        
        Returns:
            dict: {system_key: playlist_instance}
        """
        result = {}
        
        for key, config in cls.SYSTEM_PLAYLISTS.items():
            playlist, created = cls.objects.get_or_create(
                system_key=key,
                defaults={
                    'name': config['name'],
                    'description': config['description'],
                    'playlist_type': 'system',
                }
            )
            
            if created:
                print(f"[Music] Created system playlist: {config['name']}")
            
            result[key] = playlist
        
        return result
    
    @classmethod
    def get_system_playlist(cls, key: str):
        """
        Get a specific system playlist by key.
        Creates it if it doesn't exist.
        
        Args:
            key: System key like 'video_help' or 'news'
            
        Returns:
            Playlist instance or None if key is invalid
        """
        if key not in cls.SYSTEM_PLAYLISTS:
            return None
        
        config = cls.SYSTEM_PLAYLISTS[key]
        
        playlist, _ = cls.objects.get_or_create(
            system_key=key,
            defaults={
                'name': config['name'],
                'description': config['description'],
                'playlist_type': 'system',
            }
        )
        
        return playlist


class PlaylistEntry(models.Model):
    """Link between Playlist and Track with ordering"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='entries')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='playlist_entries')
    position = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
        unique_together = ['playlist', 'position']
    
    def __str__(self):
        return f"{self.playlist.name} #{self.position}: {self.track.title}"


class AudioCacheLog(models.Model):
    """
    Logs all audio cache operations.
    
    Used for:
    - Player warning during active downloads
    - Correlation with latency test anomalies
    - Detecting YouTube rate limiting/blocks
    - Network debugging
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    track = models.ForeignKey(
        Track,
        on_delete=models.SET_NULL,
        related_name='cache_logs',
        null=True,
        blank=True
    )
    video_id = models.CharField(max_length=20, db_index=True)
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('downloading', 'Downloading'),
        ('converting', 'Converting'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cached', 'Already Cached'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # === TIMESTAMPS (for anomaly correlation) ===
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # === NETWORK METRICS ===
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    download_duration_seconds = models.FloatField(null=True, blank=True)
    bandwidth_bytes_per_sec = models.FloatField(null=True, blank=True)
    
    # Download phases (for detailed analysis)
    download_started_at = models.DateTimeField(null=True, blank=True)
    download_completed_at = models.DateTimeField(null=True, blank=True)
    conversion_started_at = models.DateTimeField(null=True, blank=True)
    conversion_completed_at = models.DateTimeField(null=True, blank=True)
    
    # === ERROR TRACKING ===
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # === ADDITIONAL INFO ===
    yt_dlp_version = models.CharField(max_length=50, blank=True)
    audio_format = models.CharField(max_length=20, blank=True, default='m4a')
    audio_bitrate = models.PositiveIntegerField(null=True, blank=True, help_text="Bitrate in kbps")
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['started_at', 'completed_at']),
            models.Index(fields=['video_id', 'status']),
        ]
        verbose_name = "Audio Cache Log"
        verbose_name_plural = "Audio Cache Logs"
    
    def __str__(self):
        return f"Cache {self.video_id}: {self.status}"
    
    @property
    def is_active(self):
        """Check if download is still running."""
        return self.status in ('started', 'downloading', 'converting')
    
    @property
    def duration(self):
        """Total operation duration in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def calculate_bandwidth(self):
        """Calculate and save bandwidth if possible."""
        if self.file_size_bytes and self.download_duration_seconds:
            self.bandwidth_bytes_per_sec = self.file_size_bytes / self.download_duration_seconds
            self.save(update_fields=['bandwidth_bytes_per_sec'])
    
    # === CLASS METHODS FOR QUERIES ===
    
    @classmethod
    def get_active_downloads(cls):
        """Returns all currently active downloads."""
        return cls.objects.filter(status__in=['started', 'downloading', 'converting'])
    
    @classmethod
    def has_active_downloads(cls):
        """Check if any downloads are running (for test warning)."""
        return cls.get_active_downloads().exists()
    
    @classmethod
    def get_downloads_in_timerange(cls, start_time, end_time):
        """
        Find all downloads that were active during a time range.
        
        Useful for: "Was a download active when this latency spike occurred?"
        
        Args:
            start_time: Start of the time range
            end_time: End of the time range
            
        Returns:
            QuerySet of AudioCacheLog entries that overlapped with the time range
        """
        return cls.objects.filter(
            started_at__lte=end_time,  # Started before/during end
        ).filter(
            models.Q(completed_at__gte=start_time) |  # Ended after/during start
            models.Q(completed_at__isnull=True)  # Or still running
        )
    
    @classmethod
    def get_cache_stats(cls, days=7):
        """
        Get cache statistics for the last N days.
        
        Returns:
            dict with stats like total_downloads, failed_count, avg_bandwidth, etc.
        """
        from django.db.models import Avg, Count, Sum
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        logs = cls.objects.filter(started_at__gte=since)
        
        stats = logs.aggregate(
            total_downloads=Count('id'),
            completed_count=Count('id', filter=models.Q(status='completed')),
            failed_count=Count('id', filter=models.Q(status='failed')),
            total_bytes=Sum('file_size_bytes', filter=models.Q(status='completed')),
            avg_bandwidth=Avg('bandwidth_bytes_per_sec', filter=models.Q(status='completed')),
            avg_duration=Avg('download_duration_seconds', filter=models.Q(status='completed')),
        )
        
        # Calculate success rate
        if stats['total_downloads'] > 0:
            stats['success_rate'] = (stats['completed_count'] / stats['total_downloads']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    @classmethod
    def get_recent_failures(cls, limit=10):
        """Get recent failed downloads for debugging."""
        return cls.objects.filter(status='failed').order_by('-started_at')[:limit]


class CacheSettings(models.Model):
    """
    Singleton model for cache configuration.
    
    Only one instance should exist.
    """
    
    cache_enabled = models.BooleanField(default=True)
    max_cache_size_mb = models.PositiveIntegerField(default=10240, help_text="Max cache size in MB (default 10GB)")
    
    auto_cleanup_enabled = models.BooleanField(default=True)
    cleanup_after_days = models.PositiveIntegerField(default=30, help_text="Delete cached files older than N days")
    
    max_concurrent_downloads = models.PositiveIntegerField(default=2)
    min_delay_between_downloads = models.PositiveIntegerField(default=5, help_text="Minimum seconds between downloads (rate limit protection)")
    
    # Audio quality settings
    preferred_format = models.CharField(max_length=20, default='m4a')
    preferred_bitrate = models.PositiveIntegerField(default=128, help_text="Preferred bitrate in kbps")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cache Settings"
        verbose_name_plural = "Cache Settings"
    
    def __str__(self):
        return "Cache Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and CacheSettings.objects.exists():
            raise ValueError("Only one CacheSettings instance allowed")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings