"""
Stresstests API - ViewSets
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from stresstests.models import Test, TestResult, Metric
from .serializers import (
    TestListSerializer,
    TestDetailSerializer,
    TestResultSerializer,
    MetricSerializer,
)


class TestViewSet(viewsets.ModelViewSet):
    """
    API endpoint für Tests.
    
    GET    /api/v1/tests/                 - Liste (filter: type, status)
    POST   /api/v1/tests/                 - Erstellen
    GET    /api/v1/tests/{id}/            - Details
    PUT    /api/v1/tests/{id}/            - Aktualisieren
    DELETE /api/v1/tests/{id}/            - Löschen
    POST   /api/v1/tests/{id}/start/      - Starten
    POST   /api/v1/tests/{id}/stop/       - Stoppen
    POST   /api/v1/tests/{id}/pause/      - Pausieren
    GET    /api/v1/tests/{id}/results/    - Ergebnisse
    """
    queryset = Test.objects.prefetch_related('servers').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'test_type', 'status', 'last_run', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TestListSerializer
        return TestDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by type
        test_type = self.request.query_params.get('type')
        if test_type:
            queryset = queryset.filter(test_type=test_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Test starten"""
        test = self.get_object()
        test.activate()
        return Response({
            'id': test.id,
            'status': test.status,
            'message': f'Test {test.name} gestartet'
        })
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Test stoppen"""
        test = self.get_object()
        test.deactivate()
        return Response({
            'id': test.id,
            'status': test.status,
            'message': f'Test {test.name} gestoppt'
        })
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Test pausieren"""
        test = self.get_object()
        test.pause()
        return Response({
            'id': test.id,
            'status': test.status,
            'message': f'Test {test.name} pausiert'
        })
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Test-Ergebnisse abrufen"""
        test = self.get_object()
        results = TestResult.objects.filter(test=test).select_related('server')
        
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        
        total = results.count()
        results = results[offset:offset+limit]
        
        serializer = TestResultSerializer(results, many=True)
        return Response({
            'total': total,
            'limit': limit,
            'offset': offset,
            'results': serializer.data
        })


class TestResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint für Test-Ergebnisse (nur Lesen).
    
    GET /api/v1/results/       - Liste (filter: test, server, success, hours)
    GET /api/v1/results/{id}/  - Details
    """
    queryset = TestResult.objects.select_related('test', 'server').all()
    serializer_class = TestResultSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp', 'latency_ms']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        test_id = self.request.query_params.get('test')
        if test_id:
            queryset = queryset.filter(test_id=test_id)
        
        server_id = self.request.query_params.get('server')
        if server_id:
            queryset = queryset.filter(server_id=server_id)
        
        success = self.request.query_params.get('success')
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')
        
        hours = self.request.query_params.get('hours')
        if hours:
            since = timezone.now() - timedelta(hours=int(hours))
            queryset = queryset.filter(timestamp__gte=since)
        
        return queryset
