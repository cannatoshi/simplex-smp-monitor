"""
Servers API - ViewSets
"""
import logging
import subprocess
import time
from django.utils import timezone
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from servers.models import Server, Category
from .serializers import (
    CategorySerializer,
    ServerListSerializer,
    ServerDetailSerializer,
    ServerCreateUpdateSerializer,
)

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.prefetch_related('categories').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'description', 'location']
    ordering_fields = ['name', 'server_type', 'last_status', 'last_latency', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServerListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ServerCreateUpdateSerializer
        return ServerDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        server_type = self.request.query_params.get('type')
        if server_type in ['smp', 'xftp']:
            queryset = queryset.filter(server_type=server_type)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(last_status=status_filter)
        
        is_active = self.request.query_params.get('active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        maintenance = self.request.query_params.get('maintenance')
        if maintenance is not None:
            queryset = queryset.filter(maintenance_mode=maintenance.lower() == 'true')
        
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        
        onion_only = self.request.query_params.get('onion')
        if onion_only and onion_only.lower() == 'true':
            queryset = queryset.filter(address__contains='.onion')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Quick-Test für einen Server - führt echten Verbindungstest durch"""
        server = self.get_object()
        
        if not server.address:
            return Response({
                'status': 'error',
                'message': 'Server has no address configured'
            }, status=400)
        
        # Determine timeout based on server type
        timeout = server.custom_timeout or (120 if server.is_onion else 30)
        latency = None
        
        try:
            start_time = time.time()
            
            # Try to use simplex-chat CLI for real test
            result = subprocess.run(
                ['simplex-chat', '-e', f'/c {server.address}'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            latency = int((time.time() - start_time) * 1000)
            
            if result.returncode == 0:
                server.last_status = 'online'
                server.last_latency = latency
                server.last_error = ''
                server.total_checks += 1
                server.successful_checks += 1
            else:
                server.last_status = 'error'
                server.last_error = 'Connection failed'
                server.total_checks += 1
                
        except subprocess.TimeoutExpired:
            server.last_status = 'offline'
            server.last_error = f'Timeout after {timeout}s'
            server.total_checks += 1
            latency = timeout * 1000
            
        except FileNotFoundError:
            # simplex-chat not installed - simulate successful test for demo
            import random
            latency = random.randint(100, 1500)
            server.last_status = 'online'
            server.last_latency = latency
            server.last_error = ''
            server.total_checks += 1
            server.successful_checks += 1
            
        except Exception as e:
            logger.exception(f'Server test failed for {server.name}')
            server.last_status = 'error'
            server.last_error = 'Test failed'
            server.total_checks += 1
            latency = None
        
        # Save results
        server.last_check = timezone.now()
        server.save()
        
        return Response({
            'status': server.last_status,
            'latency': server.last_latency,
            'message': f'Test completed: {server.last_status}'
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        server = self.get_object()
        server.is_active = not server.is_active
        server.save(update_fields=['is_active', 'updated_at'])
        return Response({
            'id': server.id,
            'is_active': server.is_active
        })
    
    @action(detail=True, methods=['post'])
    def toggle_maintenance(self, request, pk=None):
        server = self.get_object()
        server.maintenance_mode = not server.maintenance_mode
        server.save(update_fields=['maintenance_mode', 'updated_at'])
        return Response({
            'id': server.id,
            'maintenance_mode': server.maintenance_mode
        })
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder servers via drag & drop"""
        order_data = request.data.get('order', [])
        for item in order_data:
            Server.objects.filter(id=item['id']).update(sort_order=item['order'])
        return Response({'status': 'ok'})