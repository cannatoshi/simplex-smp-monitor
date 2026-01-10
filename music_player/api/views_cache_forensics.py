"""
SimpleX SMP Monitor - Cache Forensics API Views
================================================
Copyright (c) 2026 cannatoshi
https://github.com/cannatoshi/simplex-smp-monitor

Extended API endpoints for cache forensics and analytics.
"""
from datetime import timedelta
from collections import defaultdict

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django.utils import timezone
from django.db.models import Count, Sum, Avg, Max, Min, F
from django.db.models.functions import TruncDate, TruncHour, ExtractHour, ExtractWeekDay

from ..models import Track, AudioCacheLog, CacheSettings
from .serializers import AudioCacheLogSerializer


class CacheHistoryPagination(PageNumberPagination):
    """Pagination for cache history."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class CacheHistoryView(APIView):
    """
    API endpoint for paginated cache download history.
    
    GET /api/v1/music/cache/history/
    
    Query params:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 50, max: 200)
        - status: Filter by status (completed, failed, etc.)
        - days: Filter last N days (default: all)
        - order: Sort order (default: -started_at)
    """
    
    def get(self, request):
        queryset = AudioCacheLog.objects.all()
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by days
        days = request.query_params.get('days')
        if days:
            try:
                days = int(days)
                cutoff = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(started_at__gte=cutoff)
            except ValueError:
                pass
        
        # Ordering
        order = request.query_params.get('order', '-started_at')
        allowed_orders = ['started_at', '-started_at', 'file_size_bytes', '-file_size_bytes', 
                         'download_duration_seconds', '-download_duration_seconds']
        if order in allowed_orders:
            queryset = queryset.order_by(order)
        
        # Paginate
        paginator = CacheHistoryPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = AudioCacheLogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = AudioCacheLogSerializer(queryset, many=True)
        return Response(serializer.data)


class CacheAnalyticsView(APIView):
    """
    API endpoint for cache analytics and graph data.
    
    GET /api/v1/music/cache/analytics/
    
    Query params:
        - days: Number of days to analyze (default: 30)
    
    Returns aggregated data for:
        - Downloads per day (line chart)
        - Bandwidth over time
        - Activity heatmap (hour x weekday)
        - File size distribution
        - Success/failure rates
    """
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        cutoff = timezone.now() - timedelta(days=days)
        
        logs = AudioCacheLog.objects.filter(started_at__gte=cutoff)
        completed_logs = logs.filter(status='completed')
        
        # === DOWNLOADS PER DAY ===
        downloads_per_day = list(
            logs
            .annotate(date=TruncDate('started_at'))
            .values('date')
            .annotate(
                total=Count('id'),
                completed=Count('id', filter=models.Q(status='completed')),
                failed=Count('id', filter=models.Q(status='failed')),
                total_bytes=Sum('file_size_bytes', filter=models.Q(status='completed'))
            )
            .order_by('date')
        )
        
        # Convert dates to strings
        for item in downloads_per_day:
            item['date'] = item['date'].isoformat() if item['date'] else None
            item['total_mb'] = round((item['total_bytes'] or 0) / 1024 / 1024, 2)
        
        # === BANDWIDTH TIMELINE ===
        # Get hourly bandwidth for the last 7 days (more granular)
        bandwidth_cutoff = timezone.now() - timedelta(days=7)
        bandwidth_timeline = list(
            completed_logs
            .filter(started_at__gte=bandwidth_cutoff)
            .annotate(hour=TruncHour('started_at'))
            .values('hour')
            .annotate(
                avg_bandwidth=Avg('bandwidth_bytes_per_sec'),
                max_bandwidth=Max('bandwidth_bytes_per_sec'),
                download_count=Count('id')
            )
            .order_by('hour')
        )
        
        for item in bandwidth_timeline:
            item['hour'] = item['hour'].isoformat() if item['hour'] else None
            item['avg_bandwidth_kbps'] = round((item['avg_bandwidth'] or 0) / 1024, 1)
            item['max_bandwidth_kbps'] = round((item['max_bandwidth'] or 0) / 1024, 1)
        
        # === ACTIVITY HEATMAP (hour x weekday) ===
        # Returns count of downloads for each hour/weekday combination
        heatmap_data = list(
            logs
            .annotate(
                hour=ExtractHour('started_at'),
                weekday=ExtractWeekDay('started_at')  # 1=Sunday, 7=Saturday
            )
            .values('hour', 'weekday')
            .annotate(count=Count('id'))
            .order_by('weekday', 'hour')
        )
        
        # === FILE SIZE DISTRIBUTION ===
        # Bucket sizes: <1MB, 1-5MB, 5-10MB, 10-20MB, >20MB
        size_buckets = {
            'tiny': 0,      # <1MB
            'small': 0,     # 1-5MB
            'medium': 0,    # 5-10MB
            'large': 0,     # 10-20MB
            'huge': 0       # >20MB
        }
        
        for log in completed_logs.filter(file_size_bytes__isnull=False):
            size_mb = log.file_size_bytes / 1024 / 1024
            if size_mb < 1:
                size_buckets['tiny'] += 1
            elif size_mb < 5:
                size_buckets['small'] += 1
            elif size_mb < 10:
                size_buckets['medium'] += 1
            elif size_mb < 20:
                size_buckets['large'] += 1
            else:
                size_buckets['huge'] += 1
        
        size_distribution = [
            {'range': '<1 MB', 'count': size_buckets['tiny']},
            {'range': '1-5 MB', 'count': size_buckets['small']},
            {'range': '5-10 MB', 'count': size_buckets['medium']},
            {'range': '10-20 MB', 'count': size_buckets['large']},
            {'range': '>20 MB', 'count': size_buckets['huge']},
        ]
        
        # === OVERALL STATS ===
        total_downloads = logs.count()
        completed_count = logs.filter(status='completed').count()
        failed_count = logs.filter(status='failed').count()
        
        stats = completed_logs.aggregate(
            total_bytes=Sum('file_size_bytes'),
            avg_bandwidth=Avg('bandwidth_bytes_per_sec'),
            max_bandwidth=Max('bandwidth_bytes_per_sec'),
            min_bandwidth=Min('bandwidth_bytes_per_sec'),
            avg_duration=Avg('download_duration_seconds'),
            total_duration=Sum('download_duration_seconds')
        )
        
        # === TOP ERRORS ===
        top_errors = list(
            logs
            .filter(status='failed')
            .exclude(error_message='')
            .values('error_message')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        # === RECENT ACTIVITY (last 24h) ===
        last_24h = timezone.now() - timedelta(hours=24)
        recent_stats = logs.filter(started_at__gte=last_24h).aggregate(
            total=Count('id'),
            completed=Count('id', filter=models.Q(status='completed')),
            failed=Count('id', filter=models.Q(status='failed')),
            total_bytes=Sum('file_size_bytes', filter=models.Q(status='completed'))
        )
        
        return Response({
            'period_days': days,
            'generated_at': timezone.now().isoformat(),
            
            # Summary
            'summary': {
                'total_downloads': total_downloads,
                'completed': completed_count,
                'failed': failed_count,
                'success_rate': round(completed_count / total_downloads * 100, 1) if total_downloads > 0 else 0,
                'total_bytes': stats['total_bytes'] or 0,
                'total_mb': round((stats['total_bytes'] or 0) / 1024 / 1024, 2),
                'total_gb': round((stats['total_bytes'] or 0) / 1024 / 1024 / 1024, 3),
                'avg_bandwidth_kbps': round((stats['avg_bandwidth'] or 0) / 1024, 1),
                'max_bandwidth_kbps': round((stats['max_bandwidth'] or 0) / 1024, 1),
                'avg_duration_seconds': round(stats['avg_duration'] or 0, 1),
                'total_duration_minutes': round((stats['total_duration'] or 0) / 60, 1),
            },
            
            # Last 24h
            'last_24h': {
                'total': recent_stats['total'] or 0,
                'completed': recent_stats['completed'] or 0,
                'failed': recent_stats['failed'] or 0,
                'total_mb': round((recent_stats['total_bytes'] or 0) / 1024 / 1024, 2),
            },
            
            # Chart data
            'downloads_per_day': downloads_per_day,
            'bandwidth_timeline': bandwidth_timeline,
            'heatmap': heatmap_data,
            'size_distribution': size_distribution,
            'top_errors': top_errors,
        })


class CacheCleanupHistoryView(APIView):
    """
    API endpoint to delete old cache logs.
    
    POST /api/v1/music/cache/history/cleanup/
    
    Body:
        - days: Delete logs older than N days
        - confirm: Must be true
    """
    
    def post(self, request):
        days = request.data.get('days', 90)
        confirm = request.data.get('confirm', False)
        
        if not confirm:
            return Response(
                {'error': 'Confirmation required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            days = int(days)
        except ValueError:
            return Response(
                {'error': 'Invalid days value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cutoff = timezone.now() - timedelta(days=days)
        
        # Count before delete
        count = AudioCacheLog.objects.filter(started_at__lt=cutoff).count()
        
        # Delete old logs
        AudioCacheLog.objects.filter(started_at__lt=cutoff).delete()
        
        return Response({
            'deleted_count': count,
            'cutoff_date': cutoff.isoformat(),
            'days': days
        })


# Need to import models for Q objects
from django.db import models