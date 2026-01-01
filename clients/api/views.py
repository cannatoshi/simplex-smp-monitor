"""
API Views für SimpleX CLI Clients
"""
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Q
from django.utils import timezone

from clients.models import SimplexClient, ClientConnection, TestMessage
from .serializers import (
    SimplexClientListSerializer,
    SimplexClientDetailSerializer,
    SimplexClientCreateUpdateSerializer,
    ClientConnectionSerializer,
    TestMessageSerializer,
    ClientStatsSerializer,
)

logger = logging.getLogger(__name__)


class SimplexClientViewSet(viewsets.ModelViewSet):
    """ViewSet für SimpleX CLI Clients"""
    queryset = SimplexClient.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SimplexClientListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SimplexClientCreateUpdateSerializer
        return SimplexClientDetailSerializer
    
    def get_queryset(self):
        queryset = SimplexClient.objects.all().order_by('name')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    def perform_destroy(self, instance):
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            docker_manager.delete_container(instance, remove_volume=False)
        except Exception:
            pass
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def start(self, request, id=None):
        client = self.get_object()
        if client.status == SimplexClient.Status.RUNNING:
            return Response({'error': f'{client.name} läuft bereits.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            docker_manager.start_container(client)
            client.start()
            return Response({'success': True, 'status': client.status, 'message': f'{client.name} wurde gestartet.'})
        except Exception as e:
            logger.exception(f'Failed to start client {client.name}')
            client.set_error(str(e))
            return Response({'error': 'Failed to start client'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, id=None):
        client = self.get_object()
        if client.status != SimplexClient.Status.RUNNING:
            return Response({'error': f'{client.name} läuft nicht.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            docker_manager.stop_container(client)
            client.stop()
            return Response({'success': True, 'status': client.status, 'message': f'{client.name} wurde gestoppt.'})
        except Exception as e:
            logger.exception(f'Failed to stop client {client.name}')
            client.set_error(str(e))
            return Response({'error': 'Failed to stop client'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def restart(self, request, id=None):
        client = self.get_object()
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            docker_manager.restart_container(client)
            client.start()
            return Response({'success': True, 'status': client.status, 'message': f'{client.name} wurde neu gestartet.'})
        except Exception as e:
            logger.exception(f'Failed to restart client {client.name}')
            client.set_error(str(e))
            return Response({'error': 'Failed to restart client'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, id=None):
        client = self.get_object()
        tail = int(request.query_params.get('tail', 50))
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            logs = docker_manager.get_container_logs(client, tail=tail) or ''
            return Response({'logs': logs[:50000], 'status': client.status})
        except Exception as e:
            logger.exception(f'Failed to get logs for client {client.name}')
            return Response({'logs': '[Error fetching logs]', 'status': client.status})
    
    @action(detail=True, methods=['get'])
    def connections(self, request, id=None):
        client = self.get_object()
        connections = ClientConnection.objects.filter(
            Q(client_a=client) | Q(client_b=client)
        ).select_related('client_a', 'client_b')
        serializer = ClientConnectionSerializer(connections, many=True)
        return Response(serializer.data)


class ClientConnectionViewSet(viewsets.ModelViewSet):
    """ViewSet für Client-Verbindungen"""
    queryset = ClientConnection.objects.all()
    serializer_class = ClientConnectionSerializer
    
    def get_queryset(self):
        queryset = ClientConnection.objects.all()
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(Q(client_a_id=client_id) | Q(client_b_id=client_id))
        return queryset.select_related('client_a', 'client_b')


class ClientStatsView(APIView):
    """API View für Client-Statistiken"""
    
    def get(self, request):
        stats = {
            'total': SimplexClient.objects.count(),
            'running': SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING).count(),
            'stopped': SimplexClient.objects.filter(status=SimplexClient.Status.STOPPED).count(),
            'error': SimplexClient.objects.filter(status=SimplexClient.Status.ERROR).count(),
            'total_messages_sent': SimplexClient.objects.aggregate(total=Sum('messages_sent'))['total'] or 0,
            'total_messages_received': SimplexClient.objects.aggregate(total=Sum('messages_received'))['total'] or 0,
        }
        used_ports = set(SimplexClient.objects.values_list('websocket_port', flat=True))
        stats['available_ports'] = [p for p in range(3031, 3081) if p not in used_ports][:5]
        serializer = ClientStatsSerializer(stats)
        return Response(serializer.data)


class TestMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet für Test-Nachrichten (nur lesen)"""
    queryset = TestMessage.objects.all()
    serializer_class = TestMessageSerializer
    
    def get_queryset(self):
        queryset = TestMessage.objects.all().select_related('sender', 'recipient', 'connection')
        
        # Filter by client (sent or received)
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(
                Q(sender_id=client_id) | Q(recipient_id=client_id)
            )
        
        # Filter by direction
        direction = self.request.query_params.get('direction')
        if direction == 'sent' and client_id:
            queryset = queryset.filter(sender_id=client_id)
        elif direction == 'received' and client_id:
            queryset = queryset.filter(recipient_id=client_id)
        
        return queryset.order_by('-created_at')[:50]