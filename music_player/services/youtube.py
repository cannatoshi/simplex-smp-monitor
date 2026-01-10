"""
SimpleX SMP Monitor - YouTube Service
=====================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

YouTube audio extraction using yt-dlp.
"""
import re
import logging
import subprocess
import json
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for extracting audio information and URLs from YouTube."""
    
    # Regex patterns for YouTube URLs/IDs
    YOUTUBE_PATTERNS = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',  # Direct video ID
    ]
    
    # Common yt-dlp options to avoid errors
    COMMON_OPTIONS = [
        '--no-check-certificates',
        '--no-warnings',
        '--prefer-free-formats',
        '--no-playlist',
        '--extractor-args', 'youtube:player_client=android,web',
    ]
    
    def __init__(self):
        self._yt_dlp_version = None
    
    @property
    def yt_dlp_version(self) -> str:
        """Get yt-dlp version string."""
        if self._yt_dlp_version is None:
            try:
                result = subprocess.run(
                    ['yt-dlp', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                self._yt_dlp_version = result.stdout.strip()
            except Exception as e:
                logger.warning(f"Could not get yt-dlp version: {e}")
                self._yt_dlp_version = "unknown"
        return self._yt_dlp_version
    
    def extract_video_id(self, url_or_id: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL or validate direct ID.
        
        Args:
            url_or_id: YouTube URL or video ID
            
        Returns:
            Video ID or None if invalid
        """
        url_or_id = url_or_id.strip()
        
        for pattern in self.YOUTUBE_PATTERNS:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_info(self, video_id: str) -> Optional[dict]:
        """
        Get video metadata without downloading.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dict with title, artist, duration, thumbnail_url or None on error
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                *self.COMMON_OPTIONS,
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"yt-dlp error for {video_id}: {result.stderr}")
                return None
            
            data = json.loads(result.stdout)
            
            # Get best thumbnail
            thumbnail = data.get('thumbnail', '')
            thumbnails = data.get('thumbnails', [])
            if thumbnails:
                # Prefer medium quality thumbnail
                for t in thumbnails:
                    if t.get('height', 0) >= 180:
                        thumbnail = t.get('url', thumbnail)
                        break
            
            return {
                'title': data.get('title', 'Unknown Title'),
                'artist': data.get('artist') or data.get('channel') or data.get('uploader', ''),
                'duration': data.get('duration'),
                'thumbnail_url': thumbnail,
                'description': data.get('description', ''),
                'filesize_approx': data.get('filesize_approx'),
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout getting info for {video_id}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {video_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting info for {video_id}: {e}")
            return None
    
    def get_audio_stream_url(self, video_id: str) -> Optional[str]:
        """
        Get direct audio stream URL (expires after ~6 hours).
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Direct audio URL or None on error
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            cmd = [
                'yt-dlp',
                '-f', 'bestaudio[ext=m4a]/bestaudio/best',
                '-g',  # Get URL only
                *self.COMMON_OPTIONS,
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"yt-dlp stream URL error for {video_id}: {result.stderr}")
                return None
            
            stream_url = result.stdout.strip()
            if stream_url:
                return stream_url
            
            return None
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout getting stream URL for {video_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting stream URL for {video_id}: {e}")
            return None
    
    def search_videos(self, query: str, max_results: int = 10) -> list:
        """
        Search YouTube for videos.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of dicts with video_id, title, artist, duration, thumbnail_url
        """
        try:
            cmd = [
                'yt-dlp',
                f'ytsearch{max_results}:{query}',
                '--dump-json',
                '--no-download',
                '--flat-playlist',
                '--no-check-certificates',
                '--no-warnings',
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"yt-dlp search error: {result.stderr}")
                return []
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    
                    # Get thumbnail
                    thumbnail = data.get('thumbnail', '')
                    thumbnails = data.get('thumbnails', [])
                    if thumbnails:
                        for t in thumbnails:
                            if t.get('height', 0) >= 180:
                                thumbnail = t.get('url', thumbnail)
                                break
                    
                    videos.append({
                        'video_id': data.get('id'),
                        'title': data.get('title', 'Unknown'),
                        'artist': data.get('channel') or data.get('uploader', ''),
                        'duration': data.get('duration'),
                        'thumbnail_url': thumbnail,
                        'filesize_approx': data.get('filesize_approx'),
                    })
                except json.JSONDecodeError:
                    continue
            
            return videos
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout searching for: {query}")
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []


# Singleton instance
youtube_service = YouTubeService()