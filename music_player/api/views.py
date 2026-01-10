"""
SimpleX SMP Monitor - Music Player API Views
=============================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

REST API endpoints for music player.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from ..models import Track, Playlist, PlaylistEntry, AudioCacheLog, CacheSettings
from ..services.youtube import youtube_service
from ..services.audio_cache import audio_cache_service
from .serializers import (
    TrackSerializer,
    TrackCreateFromYouTubeSerializer,
    PlaylistSerializer,
    PlaylistListSerializer,
    PlaylistEntrySerializer,
    AudioCacheLogSerializer,
    CacheStatusSerializer,
    CacheControlSerializer,
    CacheSettingsSerializer,
)


class TrackViewSet(viewsets.ModelViewSet):
    """API endpoint for tracks."""
    
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    
    def perform_destroy(self, instance):
        """Delete track and its cached file."""
        # Delete cached audio file
        if instance.source_id:
            audio_cache_service.delete_cached(instance.source_id)
        
        # Delete associated logs
        AudioCacheLog.objects.filter(track=instance).delete()
        
        # Delete track
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def stream(self, request, pk=None):
        """
        Get audio stream URL for a track.
        
        Returns cached file URL if available, otherwise YouTube stream URL.
        Priority: Local cache > YouTube stream
        """
        track = self.get_object()
        
        if track.source_type != 'youtube':
            return Response(
                {'error': 'Only YouTube tracks supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if cached locally (any format)
        cached_url = audio_cache_service.get_cached_url(track.source_id)
        
        if cached_url:
            # Update track.is_cached if needed
            if not track.is_cached:
                track.is_cached = True
                track.cached_at = track.cached_at or __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()
                track.save(update_fields=['is_cached', 'cached_at'])
            
            # Increment play count
            track.play_count += 1
            track.save(update_fields=['play_count'])
            
            return Response({
                'source': 'cache',
                'url': cached_url,
                'cached': True
            })
        
        # Not cached - get YouTube stream URL
        stream_url = youtube_service.get_audio_stream_url(track.source_id)
        
        if not stream_url:
            return Response(
                {'error': 'Could not get stream URL. Try caching the track first.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Increment play count
        track.play_count += 1
        track.save(update_fields=['play_count'])
        
        return Response({
            'source': 'youtube',
            'url': stream_url,
            'cached': False
        })
    
    @action(detail=True, methods=['post'])
    def cache(self, request, pk=None):
        """Start caching audio for a track."""
        track = self.get_object()
        
        if track.source_type != 'youtube':
            return Response(
                {'error': 'Only YouTube tracks supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already cached
        if audio_cache_service.is_cached(track.source_id):
            return Response({
                'status': 'already_cached',
                'message': 'Track is already cached'
            })
        
        # Start download
        cache_path, log = audio_cache_service.get_or_download(track)
        
        if log is None:
            return Response(
                {'error': 'Max concurrent downloads reached. Try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        return Response({
            'status': log.status,
            'log_id': str(log.id),
            'cached': cache_path is not None
        })
    
    @action(detail=False, methods=['post'])
    def add_from_youtube(self, request):
        """
        Add a new track from YouTube URL or ID.
        
        Set auto_cache=true to automatically start caching after adding.
        """
        serializer = TrackCreateFromYouTubeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        url_or_id = serializer.validated_data['url_or_id']
        auto_cache = serializer.validated_data.get('auto_cache', True)  # Default TRUE now
        
        # Extract video ID
        video_id = youtube_service.extract_video_id(url_or_id)
        
        if not video_id:
            return Response(
                {'error': 'Invalid YouTube URL or ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if track already exists
        existing = Track.objects.filter(source_type='youtube', source_id=video_id).first()
        if existing:
            # Auto-cache existing track if requested and not cached
            if auto_cache and not audio_cache_service.is_cached(video_id):
                audio_cache_service.get_or_download(existing)
            
            return Response({
                'status': 'exists',
                'track': TrackSerializer(existing).data
            })
        
        # Get video info
        info = youtube_service.get_video_info(video_id)
        
        if not info:
            return Response(
                {'error': 'Could not fetch video info. YouTube may be blocking requests.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Create track
        track = Track.objects.create(
            source_type='youtube',
            source_id=video_id,
            title=info['title'],
            artist=info['artist'],
            duration=info['duration'],
            thumbnail_url=info['thumbnail_url']
        )
        
        # Auto-cache (default behavior now)
        cache_status = None
        if auto_cache:
            cache_path, log = audio_cache_service.get_or_download(track)
            cache_status = log.status if log else 'queued'
        
        return Response({
            'status': 'created',
            'track': TrackSerializer(track).data,
            'cache_status': cache_status
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search YouTube for videos."""
        query = request.query_params.get('q', '')
        max_results = int(request.query_params.get('limit', 10))
        
        if not query:
            return Response(
                {'error': 'Search query required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = youtube_service.search_videos(query, max_results)
        
        # Mark which results are already in library
        video_ids = [r['video_id'] for r in results]
        existing_ids = set(
            Track.objects.filter(source_id__in=video_ids)
            .values_list('source_id', flat=True)
        )
        
        for result in results:
            result['in_library'] = result['video_id'] in existing_ids
        
        return Response({
            'query': query,
            'count': len(results),
            'results': results
        })


class PlaylistViewSet(viewsets.ModelViewSet):
    """API endpoint for playlists."""
    
    queryset = Playlist.objects.all()
    
    def get_queryset(self):
        """Ensure system playlists exist on every request."""
        # Auto-create system playlists if they don't exist
        Playlist.ensure_system_playlists()
        return Playlist.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PlaylistListSerializer
        return PlaylistSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Prevent deletion of system playlists."""
        playlist = self.get_object()
        
        if playlist.is_system_playlist:
            return Response(
                {'error': 'System playlists cannot be deleted'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def system(self, request):
        """Get all system playlists."""
        # Ensure they exist
        Playlist.ensure_system_playlists()
        
        system_playlists = Playlist.objects.filter(playlist_type='system')
        serializer = PlaylistSerializer(system_playlists, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='system/(?P<system_key>[^/.]+)')
    def system_by_key(self, request, system_key=None):
        """Get a specific system playlist by key."""
        playlist = Playlist.get_system_playlist(system_key)
        
        if not playlist:
            return Response(
                {'error': f'Unknown system playlist key: {system_key}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_track(self, request, pk=None):
        """Add a track to the playlist."""
        playlist = self.get_object()
        track_id = request.data.get('track_id')
        
        if not track_id:
            return Response(
                {'error': 'track_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        track = get_object_or_404(Track, pk=track_id)
        
        # Get next position
        last_entry = playlist.entries.order_by('-position').first()
        next_position = (last_entry.position + 1) if last_entry else 0
        
        entry = PlaylistEntry.objects.create(
            playlist=playlist,
            track=track,
            position=next_position
        )
        
        return Response({
            'status': 'added',
            'entry': PlaylistEntrySerializer(entry).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_track(self, request, pk=None):
        """Remove a track from the playlist."""
        playlist = self.get_object()
        entry_id = request.data.get('entry_id')
        
        if not entry_id:
            return Response(
                {'error': 'entry_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entry = get_object_or_404(PlaylistEntry, pk=entry_id, playlist=playlist)
        entry.delete()
        
        # Reorder remaining entries
        for i, e in enumerate(playlist.entries.order_by('position')):
            if e.position != i:
                e.position = i
                e.save(update_fields=['position'])
        
        return Response({'status': 'removed'})
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder tracks in the playlist."""
        playlist = self.get_object()
        order = request.data.get('order', [])
        
        if not order:
            return Response(
                {'error': 'order list required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        for position, entry_id in enumerate(order):
            PlaylistEntry.objects.filter(
                pk=entry_id,
                playlist=playlist
            ).update(position=position)
        
        return Response({'status': 'reordered'})


class CacheStatusView(APIView):
    """API endpoint for cache status (used by player)."""
    
    def get(self, request):
        """Get current cache status."""
        # Cleanup stale logs first
        audio_cache_service.cleanup_orphaned_logs()
        
        active_downloads = AudioCacheLog.get_active_downloads()
        recent_failures = AudioCacheLog.get_recent_failures(limit=5)
        stats = AudioCacheLog.get_cache_stats(days=7)
        cache_size = audio_cache_service.get_cache_size()
        
        data = {
            'is_caching': active_downloads.exists(),
            'active_downloads_count': active_downloads.count(),
            'active_downloads': AudioCacheLogSerializer(active_downloads, many=True).data,
            'recent_failures': AudioCacheLogSerializer(recent_failures, many=True).data,
            'stats': {
                **stats,
                'cache_size': cache_size
            }
        }
        
        return Response(data)


class CacheControlView(APIView):
    """API endpoint for cache control actions."""
    
    def post(self, request):
        """Execute cache control action."""
        serializer = CacheControlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.validated_data['action']
        confirm = serializer.validated_data.get('confirm', False)
        
        if action == 'cleanup':
            result = audio_cache_service.cleanup_old_cache()
            return Response({
                'action': 'cleanup',
                'result': result
            })
        
        elif action == 'toggle':
            settings = CacheSettings.get_settings()
            settings.cache_enabled = not settings.cache_enabled
            settings.save(update_fields=['cache_enabled'])
            return Response({
                'action': 'toggle',
                'cache_enabled': settings.cache_enabled
            })
        
        elif action == 'clear_all':
            if not confirm:
                return Response(
                    {'error': 'Confirmation required for clear_all'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete all cached files
            cache_size = audio_cache_service.get_cache_size()
            
            for track in Track.objects.filter(is_cached=True):
                audio_cache_service.delete_cached(track.source_id)
                track.is_cached = False
                track.cached_at = None
                track.cache_file_path = ''
                track.save(update_fields=['is_cached', 'cached_at', 'cache_file_path'])
            
            return Response({
                'action': 'clear_all',
                'deleted_count': cache_size['file_count'],
                'freed_bytes': cache_size['total_bytes']
            })
        
        elif action == 'cancel_active':
            active = AudioCacheLog.get_active_downloads()
            count = active.count()
            active.update(status='cancelled')
            return Response({
                'action': 'cancel_active',
                'cancelled_count': count
            })
        
        elif action == 'cleanup_logs':
            # New action to cleanup orphaned/stale logs
            count = audio_cache_service.cleanup_orphaned_logs()
            return Response({
                'action': 'cleanup_logs',
                'cleaned_count': count
            })
        
        return Response(
            {'error': 'Unknown action'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CacheSettingsView(APIView):
    """API endpoint for cache settings."""
    
    def get(self, request):
        """Get current cache settings."""
        settings = CacheSettings.get_settings()
        return Response(CacheSettingsSerializer(settings).data)
    
    def patch(self, request):
        """Update cache settings."""
        settings = CacheSettings.get_settings()
        serializer = CacheSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LatencyCorrelationView(APIView):
    """API endpoint for correlating cache downloads with latency anomalies."""
    
    def get(self, request):
        """
        Find cache downloads active during a time range.
        
        Query params:
            start: ISO timestamp
            end: ISO timestamp
        """
        from django.utils.dateparse import parse_datetime
        
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        
        if not start or not end:
            return Response(
                {'error': 'start and end timestamps required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start_time = parse_datetime(start)
        end_time = parse_datetime(end)
        
        if not start_time or not end_time:
            return Response(
                {'error': 'Invalid timestamp format (use ISO format)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        downloads = AudioCacheLog.get_downloads_in_timerange(start_time, end_time)
        
        return Response({
            'start': start,
            'end': end,
            'downloads_found': downloads.count(),
            'downloads': AudioCacheLogSerializer(downloads, many=True).data,
            'network_impact': downloads.filter(status__in=['downloading', 'started']).exists()
        })