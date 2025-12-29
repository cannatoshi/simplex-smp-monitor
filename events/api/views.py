"""
Events API - ViewSets
"""
from rest_framework import viewsets, filters
from django.utils import timezone
from datetime import timedelta

from events.models import EventLog
from .serializers import EventLogSerializer


class EventLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint für Event-Logs (nur Lesen).
    
    GET /api/v1/events/       - Liste (filter: level, source, hours)
    GET /api/v1/events/{id}/  - Details
    """
    queryset = EventLog.objects.all()
    serializer_class = EventLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['source', 'message']
    ordering_fields = ['created_at', 'level']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level.upper())
        
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source__icontains=source)
        
        hours = self.request.query_params.get('hours')
        if hours:
            since = timezone.now() - timedelta(hours=int(hours))
            queryset = queryset.filter(created_at__gte=since)
        
        return queryset
