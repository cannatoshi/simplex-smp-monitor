"""
SimpleX SMP Monitor - Audio Cache Service
==========================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

Local audio caching with download tracking for latency test correlation.
"""
import os
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import timedelta
from typing import Optional, Tuple, List

from django.conf import settings
from django.utils import timezone

from ..models import Track, AudioCacheLog, CacheSettings
from .youtube import youtube_service

logger = logging.getLogger(__name__)


class AudioCacheService:
    """Service for caching audio files locally."""
    
    # Supported audio formats - MP3 first for browser compatibility
    AUDIO_FORMATS = ['mp3', 'm4a', 'opus', 'webm', 'ogg', 'wav']
    
    def __init__(self):
        self._cache_dir = None
    
    @property
    def cache_dir(self) -> Path:
        """Get or create cache directory."""
        if self._cache_dir is None:
            self._cache_dir = Path(settings.BASE_DIR) / 'media' / 'audio_cache'
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        return self._cache_dir
    
    def get_cache_path(self, video_id: str, format: str = 'mp3') -> Path:
        """Get path for cached audio file."""
        return self.cache_dir / f"{video_id}.{format}"
    
    def find_cached_file(self, video_id: str) -> Optional[Path]:
        """
        Find cached audio file regardless of extension.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Path to cached file or None
        """
        for ext in self.AUDIO_FORMATS:
            cache_path = self.cache_dir / f"{video_id}.{ext}"
            if cache_path.exists() and cache_path.stat().st_size > 0:
                return cache_path
        return None
    
    def is_cached(self, video_id: str) -> bool:
        """Check if audio is already cached (any format)."""
        return self.find_cached_file(video_id) is not None
    
    def get_cached_url(self, video_id: str) -> Optional[str]:
        """
        Get URL for cached audio file.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            URL path to cached file or None
        """
        cached_file = self.find_cached_file(video_id)
        if cached_file:
            return f'/media/audio_cache/{cached_file.name}'
        return None
    
    def get_or_download(self, track: Track) -> Tuple[Optional[Path], Optional[AudioCacheLog]]:
        """
        Get cached audio or download if not available.
        
        Args:
            track: Track model instance
            
        Returns:
            Tuple of (file_path, cache_log) or (None, cache_log) on error
        """
        video_id = track.source_id
        
        # Check if already cached (any format)
        cached_file = self.find_cached_file(video_id)
        if cached_file:
            log = AudioCacheLog.objects.create(
                track=track,
                video_id=video_id,
                status='cached',
                completed_at=timezone.now()
            )
            
            # Update track if needed
            if not track.is_cached:
                track.is_cached = True
                track.cached_at = timezone.now()
                track.cache_file_path = str(cached_file)
                track.save(update_fields=['is_cached', 'cached_at', 'cache_file_path'])
            
            return cached_file, log
        
        # Check concurrent download limit
        cache_settings = CacheSettings.get_settings()
        active_count = AudioCacheLog.get_active_downloads().count()
        
        if active_count >= cache_settings.max_concurrent_downloads:
            logger.warning(f"Max concurrent downloads reached ({active_count})")
            return None, None
        
        # Start download
        return self._download_audio(track)
    
    def _download_audio(self, track: Track) -> Tuple[Optional[Path], AudioCacheLog]:
        """
        Download audio using yt-dlp.
        
        IMPORTANT: Always use MP3 format for browser compatibility!
        M4A/AAC doesn't work reliably in browsers.
        
        Args:
            track: Track model instance
            
        Returns:
            Tuple of (file_path, cache_log)
        """
        video_id = track.source_id
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        cache_settings = CacheSettings.get_settings()
        
        # FORCE MP3 for browser compatibility - ignore settings
        # M4A doesn't work in most browsers!
        preferred_format = 'mp3'
        bitrate = cache_settings.preferred_bitrate or 192
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = self.cache_dir / f"{video_id}.{preferred_format}"
        
        # Create log entry
        log = AudioCacheLog.objects.create(
            track=track,
            video_id=video_id,
            status='started',
            yt_dlp_version=youtube_service.yt_dlp_version,
            audio_format=preferred_format
        )
        
        try:
            # Update status
            log.status = 'downloading'
            log.download_started_at = timezone.now()
            log.save(update_fields=['status', 'download_started_at'])
            
            # Build yt-dlp command - FORCE MP3 output
            cmd = [
                'yt-dlp',
                '-x',  # Extract audio
                '--audio-format', 'mp3',  # ALWAYS MP3
                '--audio-quality', f'{bitrate}K',  # Bitrate in kbps
                '--no-playlist',
                '--no-check-certificates',
                '--no-warnings',
                '--extractor-args', 'youtube:player_client=android,web',
                '-o', str(output_path),
                '--force-overwrites',
                url
            ]
            
            logger.info(f"Starting download for {video_id}: {' '.join(cmd)}")
            
            # Run download
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            log.download_completed_at = timezone.now()
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                logger.error(f"yt-dlp error for {video_id}: {error_msg}")
                raise Exception(f"yt-dlp error: {error_msg[:200]}")
            
            # Find the actual output file
            cached_file = self.find_cached_file(video_id)
            
            if not cached_file:
                # List directory to debug
                files = list(self.cache_dir.glob(f"{video_id}*"))
                logger.error(f"Downloaded file not found. Files in cache: {files}")
                raise Exception(f"Downloaded file not found after yt-dlp completed. Dir contents: {files}")
            
            # Get file stats
            file_size = cached_file.stat().st_size
            download_duration = (log.download_completed_at - log.download_started_at).total_seconds()
            
            # Update track
            track.is_cached = True
            track.cached_at = timezone.now()
            track.cache_file_path = str(cached_file)
            track.save(update_fields=['is_cached', 'cached_at', 'cache_file_path'])
            
            # Update log
            log.status = 'completed'
            log.completed_at = timezone.now()
            log.file_size_bytes = file_size
            log.download_duration_seconds = download_duration
            log.bandwidth_bytes_per_sec = file_size / download_duration if download_duration > 0 else None
            log.save()
            
            logger.info(f"Cached audio for {video_id}: {file_size / 1024 / 1024:.2f} MB in {download_duration:.1f}s")
            return cached_file, log
            
        except subprocess.TimeoutExpired:
            log.status = 'failed'
            log.error_message = 'Download timeout (10 minutes exceeded)'
            log.error_code = 'TIMEOUT'
            log.completed_at = timezone.now()
            log.save()
            logger.error(f"Timeout downloading {video_id}")
            return None, log
            
        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)[:500]
            log.error_code = 'DOWNLOAD_ERROR'
            log.completed_at = timezone.now()
            log.save()
            logger.error(f"Error downloading {video_id}: {e}")
            return None, log
    
    def delete_cached(self, video_id: str) -> bool:
        """Delete cached audio file (any format)."""
        deleted = False
        for ext in self.AUDIO_FORMATS:
            cache_path = self.cache_dir / f"{video_id}.{ext}"
            if cache_path.exists():
                try:
                    cache_path.unlink()
                    logger.info(f"Deleted cached audio: {video_id}.{ext}")
                    deleted = True
                except Exception as e:
                    logger.error(f"Error deleting cached audio {video_id}.{ext}: {e}")
        return deleted
    
    def cleanup_old_cache(self, days: Optional[int] = None) -> dict:
        """
        Remove cached files older than N days.
        
        Args:
            days: Days to keep (uses settings if None)
            
        Returns:
            Dict with deleted_count, freed_bytes, errors
        """
        cache_settings = CacheSettings.get_settings()
        days = days or cache_settings.cleanup_after_days
        cutoff = timezone.now() - timedelta(days=days)
        
        result = {
            'deleted_count': 0,
            'freed_bytes': 0,
            'errors': []
        }
        
        # Find old tracks
        old_tracks = Track.objects.filter(
            is_cached=True,
            cached_at__lt=cutoff
        )
        
        for track in old_tracks:
            if self.delete_cached(track.source_id):
                result['deleted_count'] += 1
            
            # Update track
            track.is_cached = False
            track.cached_at = None
            track.cache_file_path = ''
            track.save(update_fields=['is_cached', 'cached_at', 'cache_file_path'])
        
        # Also cleanup orphaned log entries
        AudioCacheLog.objects.filter(track__isnull=True).delete()
        
        # Cleanup stale downloads
        try:
            stale_cutoff = timezone.now() - timedelta(hours=1)
            AudioCacheLog.objects.filter(
                status__in=['started', 'downloading'],
                started_at__lt=stale_cutoff
            ).update(status='failed', error_message='Stale download (timeout)', completed_at=timezone.now())
        except Exception as e:
            logger.warning(f"Could not cleanup stale logs: {e}")
        
        logger.info(f"Cache cleanup: deleted {result['deleted_count']} files")
        return result
    
    def get_cache_size(self) -> dict:
        """Get current cache size statistics."""
        total_size = 0
        file_count = 0
        
        if self.cache_dir.exists():
            for file in self.cache_dir.iterdir():
                if file.is_file() and file.suffix.lstrip('.') in self.AUDIO_FORMATS:
                    total_size += file.stat().st_size
                    file_count += 1
        
        cache_settings = CacheSettings.get_settings()
        max_size = cache_settings.max_cache_size_mb * 1024 * 1024
        
        return {
            'total_bytes': total_size,
            'total_mb': round(total_size / 1024 / 1024, 2),
            'file_count': file_count,
            'max_bytes': max_size,
            'max_mb': cache_settings.max_cache_size_mb,
            'usage_percent': round((total_size / max_size * 100), 1) if max_size > 0 else 0
        }
    
    def cleanup_orphaned_logs(self) -> int:
        """Remove log entries for tracks that no longer exist."""
        deleted_count, _ = AudioCacheLog.objects.filter(track__isnull=True).delete()
        
        # Mark stale downloads as failed
        stale_cutoff = timezone.now() - timedelta(hours=1)
        try:
            AudioCacheLog.objects.filter(
                status__in=['started', 'downloading'],
                started_at__lt=stale_cutoff
            ).update(
                status='failed',
                error_message='Stale download cleaned up',
                completed_at=timezone.now()
            )
        except Exception as e:
            logger.warning(f"Could not cleanup stale downloads: {e}")
        
        return deleted_count


# Singleton instance
audio_cache_service = AudioCacheService()