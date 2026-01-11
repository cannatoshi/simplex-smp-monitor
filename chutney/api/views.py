"""
Chutney API Views

REST API ViewSets für:
- TorNetwork: CRUD + Start/Stop/Delete Actions
- TorNode: Read + Start/Stop/Logs Actions
- TrafficCapture: Read + Download
- CircuitEvent: Read + Filter
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import logging
import os

from chutney.models import TorNetwork, TorNode, TrafficCapture, CircuitEvent
from .serializers import (
    TorNetworkListSerializer,
    TorNetworkDetailSerializer,
    TorNetworkCreateSerializer,
    TorNodeListSerializer,
    TorNodeDetailSerializer,
    TrafficCaptureListSerializer,
    TrafficCaptureDetailSerializer,
    CircuitEventSerializer,
    NetworkActionSerializer,
    NodeActionSerializer,
    CaptureActionSerializer,
)

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """CSRF-Exempt für API Calls vom React Frontend"""
    def enforce_csrf(self, request):
        return


# =============================================================================
# TorNetwork ViewSet
# =============================================================================

class TorNetworkViewSet(viewsets.ModelViewSet):
    """
    ViewSet für TorNetwork mit Docker-Management.
    
    Standard CRUD plus:
    - POST /networks/{id}/action/ - Create/Start/Stop/Delete Network
    - GET /networks/{id}/status/ - Detaillierter Status
    - GET /networks/{id}/topology/ - Netzwerk-Topologie für Visualisierung
    """
    queryset = TorNetwork.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication]
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TorNetworkListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TorNetworkCreateSerializer
        return TorNetworkDetailSerializer
    
    def get_queryset(self):
        queryset = TorNetwork.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by template
        template = self.request.query_params.get('template')
        if template:
            queryset = queryset.filter(template=template)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def network_action(self, request, pk=None):
        """
        Führt eine Aktion auf dem Netzwerk aus.
        
        Actions:
        - create: Erstellt Docker-Netzwerk und Nodes
        - start: Startet alle Nodes
        - stop: Stoppt alle Nodes
        - restart: Stop + Start
        - delete: Löscht alles (optional mit Volumes)
        """
        network = self.get_object()
        serializer = NetworkActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action_type = serializer.validated_data['action']
        remove_volumes = serializer.validated_data.get('remove_volumes', False)
        
        try:
            from chutney.services import get_chutnex_manager
            manager = get_chutnex_manager()
            
            success = False
            message = ''
            
            if action_type == 'create':
                success = manager.start_network(network)
                message = 'Network created' if success else 'Failed to create network'
            
            elif action_type == 'start':
                success = manager.start_network(network)
                message = 'Network started' if success else 'Failed to start network'
            
            elif action_type == 'stop':
                success = manager.stop_network(network)
                message = 'Network stopped' if success else 'Failed to stop network'
            
            elif action_type == 'restart':
                manager.stop_network(network)
                success = manager.start_network(network)
                message = 'Network restarted' if success else 'Failed to restart network'
            
            elif action_type == 'delete':
                success = manager.delete_network(network)
                message = 'Network deleted' if success else 'Failed to delete network'
            
            network.refresh_from_db()
            
            return Response({
                'success': success,
                'message': message,
                'status': network.status,
                'status_display': network.status_display,
            })
            
        except Exception as e:
            logger.exception(f"Network action error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def status_detail(self, request, pk=None):
        """Detaillierter Netzwerk-Status"""
        network = self.get_object()
        
        nodes_by_type = {}
        for node in network.nodes.all():
            node_type = node.get_node_type_display()
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append({
                'id': str(node.id),
                'name': node.name,
                'status': node.status,
                'status_display': node.status_display,
                'bootstrap_progress': node.bootstrap_progress,
            })
        
        return Response({
            'network': {
                'id': str(network.id),
                'name': network.name,
                'status': network.status,
                'status_display': network.status_display,
                'bootstrap_progress': network.bootstrap_progress,
                'consensus_valid': network.consensus_valid,
            },
            'nodes_by_type': nodes_by_type,
            'total_nodes': network.total_nodes,
            'running_nodes': network.running_nodes_count,
        })
    
    @action(detail=True, methods=['get'])
    def topology(self, request, pk=None):
        """
        Netzwerk-Topologie für Visualisierung.
        
        Gibt Nodes und Connections für Graph-Darstellung zurück.
        """
        network = self.get_object()
        
        nodes = []
        edges = []
        
        for node in network.nodes.all():
            nodes.append({
                'id': str(node.id),
                'label': node.name,
                'type': node.node_type,
                'icon': node.node_type_icon,
                'status': node.status,
                'group': node.node_type,
            })
        
        # Simplified edges (in reality würden wir Circuit-Daten nutzen)
        # Für jetzt: DAs verbunden mit allen Relays, Clients mit Guards
        das = [n for n in network.nodes.all() if n.node_type == 'da']
        relays = [n for n in network.nodes.all() if n.node_type in ['guard', 'middle', 'exit']]
        clients = [n for n in network.nodes.all() if n.node_type in ['client', 'hs']]
        
        # DAs untereinander verbunden (Konsens)
        for i, da1 in enumerate(das):
            for da2 in das[i+1:]:
                edges.append({
                    'from': str(da1.id),
                    'to': str(da2.id),
                    'type': 'consensus',
                })
        
        # Relays verbunden mit DAs
        for relay in relays:
            for da in das:
                edges.append({
                    'from': str(relay.id),
                    'to': str(da.id),
                    'type': 'directory',
                })
        
        return Response({
            'nodes': nodes,
            'edges': edges,
        })


# =============================================================================
# TorNode ViewSet
# =============================================================================

class TorNodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für TorNode (Read-Only + Actions).
    
    Nodes werden via TorNetwork erstellt, daher kein direktes Create/Delete.
    
    Actions:
    - POST /nodes/{id}/action/ - Start/Stop/Restart Node
    - GET /nodes/{id}/logs/ - Container Logs
    """
    queryset = TorNode.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TorNodeListSerializer
        return TorNodeDetailSerializer
    
    def get_queryset(self):
        queryset = TorNode.objects.all().select_related('network')
        
        # Filter by network
        network_id = self.request.query_params.get('network')
        if network_id:
            queryset = queryset.filter(network_id=network_id)
        
        # Filter by type
        node_type = self.request.query_params.get('type')
        if node_type:
            queryset = queryset.filter(node_type=node_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('network', 'node_type', 'index')
    
    @action(detail=True, methods=['post'])
    def node_action(self, request, pk=None):
        """
        Führt eine Aktion auf dem Node aus.
        
        Actions:
        - start: Startet den Node-Container
        - stop: Stoppt den Node-Container
        - restart: Stop + Start
        """
        node = self.get_object()
        serializer = NodeActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action_type = serializer.validated_data['action']
        remove_volumes = serializer.validated_data.get('remove_volumes', False)
        
        try:
            from chutney.services import get_chutnex_manager
            manager = get_chutnex_manager()
            
            success = False
            message = ''
            
            if action_type == 'start':
                success = manager.start_node(node)
                message = 'Node started' if success else 'Failed to start node'
            
            elif action_type == 'stop':
                success = manager.stop_node(node)
                message = 'Node stopped' if success else 'Failed to stop node'
            
            elif action_type == 'restart':
                manager.stop_node(node)
                success = manager.start_node(node)
                message = 'Node restarted' if success else 'Failed to restart node'
            
            elif action_type == 'delete':
                success = manager.delete_node(node)
                message = 'Node deleted' if success else 'Failed to delete node'
            
            node.refresh_from_db()
            
            return Response({
                'success': success,
                'message': message,
                'status': node.status,
                'status_display': node.status_display,
            })
            
        except Exception as e:
            logger.exception(f"Node action error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Holt Container-Logs"""
        node = self.get_object()
        tail = int(request.query_params.get('tail', 100))
        
        try:
            from chutney.services import get_chutnex_manager
            manager = get_chutnex_manager()
            
            logs = manager.get_node_logs(node, tail=tail)
            
            return Response({
                'logs': logs,
                'node_name': node.name,
                'container_name': node.container_name,
                'status': node.status,
            })
            
        except Exception as e:
            return Response({
                'logs': f'Error: {str(e)}',
                'node_name': node.name,
                'status': node.status,
            })
    
    @action(detail=True, methods=['get'])
    def bandwidth(self, request, pk=None):
        """Aktuelle Bandwidth-Statistiken"""
        node = self.get_object()
        
        return Response({
            'bytes_read': node.bytes_read,
            'bytes_written': node.bytes_written,
            'total': node.total_bandwidth,
            'rate': node.bandwidth_rate,
            'burst': node.bandwidth_burst,
            'circuits_active': node.circuits_active,
        })


# =============================================================================
# TrafficCapture ViewSet
# =============================================================================

class TrafficCaptureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für TrafficCapture (Read-Only + Download).
    
    Actions:
    - GET /captures/{id}/download/ - PCAP-Datei herunterladen
    - POST /captures/{id}/action/ - Start/Stop/Analyze
    """
    queryset = TrafficCapture.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TrafficCaptureListSerializer
        return TrafficCaptureDetailSerializer
    
    def get_queryset(self):
        queryset = TrafficCapture.objects.all().select_related('node', 'node__network')
        
        # Filter by node
        node_id = self.request.query_params.get('node')
        if node_id:
            queryset = queryset.filter(node_id=node_id)
        
        # Filter by network
        network_id = self.request.query_params.get('network')
        if network_id:
            queryset = queryset.filter(node__network_id=network_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-started_at')
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """PCAP-Datei herunterladen"""
        capture = self.get_object()
        
        if not capture.file_path or not os.path.exists(capture.file_path):
            return Response(
                {'error': 'Capture file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return FileResponse(
            open(capture.file_path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(capture.file_path)
        )
    
    @action(detail=True, methods=['post'])
    def capture_action(self, request, pk=None):
        """
        Führt eine Aktion auf dem Capture aus.
        
        Actions:
        - stop: Stoppt laufende Aufnahme
        - analyze: Startet Analyse (TODO)
        - delete: Löscht Capture und Datei
        """
        capture = self.get_object()
        serializer = CaptureActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action_type = serializer.validated_data['action']
        
        # TODO: Implementiere Capture-Aktionen
        
        return Response({
            'success': False,
            'message': f'Action {action_type} not yet implemented',
        })


# =============================================================================
# CircuitEvent ViewSet
# =============================================================================

class CircuitEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für CircuitEvent (Read-Only).
    
    Filter:
    - network: Filter by network ID
    - circuit_id: Filter by circuit ID
    - event_type: launched, built, failed, closed
    """
    queryset = CircuitEvent.objects.all()
    serializer_class = CircuitEventSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]
    
    def get_queryset(self):
        queryset = CircuitEvent.objects.all().select_related('network', 'source_node')
        
        # Filter by network
        network_id = self.request.query_params.get('network')
        if network_id:
            queryset = queryset.filter(network_id=network_id)
        
        # Filter by circuit ID
        circuit_id = self.request.query_params.get('circuit_id')
        if circuit_id:
            queryset = queryset.filter(circuit_id=circuit_id)
        
        # Filter by event type
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by purpose
        purpose = self.request.query_params.get('purpose')
        if purpose:
            queryset = queryset.filter(purpose=purpose)
        
        return queryset.order_by('-event_time')[:1000]  # Limit für Performance