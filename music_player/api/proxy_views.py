"""
SimpleX SMP Monitor - Audio Stream Proxy
=========================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

Proxy for YouTube audio streams to bypass CORS restrictions.
"""
import logging
import requests
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from music_player.models import Track
from music_player.services.youtube import youtube_service

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def proxy_audio_stream(request, track_id):
    """
    Proxy YouTube audio stream to bypass CORS.
    
    This fetches the audio from YouTube and streams it to the client,
    adding proper CORS headers so the browser can play it.
    """
    try:
        track = Track.objects.get(id=track_id)
    except Track.DoesNotExist:
        return JsonResponse({'error': 'Track not found'}, status=404)
    
    # Get stream URL from YouTube
    try:
        youtube_url = youtube_service.get_audio_stream_url(track.source_id)
        if not youtube_url:
            return JsonResponse({'error': 'Could not get stream URL'}, status=500)
    except Exception as e:
        logger.error(f"Error getting stream URL for {track.source_id}: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
    # Handle range requests for seeking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    # Forward range header if present (for seeking)
    range_header = request.META.get('HTTP_RANGE')
    if range_header:
        headers['Range'] = range_header
    
    try:
        # Stream from YouTube
        youtube_response = requests.get(
            youtube_url, 
            headers=headers, 
            stream=True,
            timeout=30
        )
        
        # Determine content type
        content_type = youtube_response.headers.get('Content-Type', 'audio/mp4')
        
        # Create streaming response
        def generate():
            for chunk in youtube_response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        # Set status code (206 for partial content with range requests)
        status_code = youtube_response.status_code
        
        response = StreamingHttpResponse(
            generate(),
            content_type=content_type,
            status=status_code
        )
        
        # Copy important headers
        if 'Content-Length' in youtube_response.headers:
            response['Content-Length'] = youtube_response.headers['Content-Length']
        if 'Content-Range' in youtube_response.headers:
            response['Content-Range'] = youtube_response.headers['Content-Range']
        if 'Accept-Ranges' in youtube_response.headers:
            response['Accept-Ranges'] = youtube_response.headers['Accept-Ranges']
        else:
            response['Accept-Ranges'] = 'bytes'
        
        # CORS headers
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Range'
        response['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, Accept-Ranges'
        
        return response
        
    except requests.Timeout:
        return JsonResponse({'error': 'YouTube stream timeout'}, status=504)
    except requests.RequestException as e:
        logger.error(f"Error proxying stream for {track.source_id}: {e}")
        return JsonResponse({'error': f'Stream error: {str(e)}'}, status=502)