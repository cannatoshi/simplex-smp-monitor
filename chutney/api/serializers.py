"""
Chutney API Serializers

REST Framework Serializers für:
- TorNetwork (CRUD + Actions)
- TorNode (Read + Actions)
- TrafficCapture (Read + Download)
- CircuitEvent (Read)
"""

from rest_framework import serializers
from chutney.models import TorNetwork, TorNode, TrafficCapture, CircuitEvent


# =============================================================================
# TorNetwork Serializers
# =============================================================================

class TorNetworkListSerializer(serializers.ModelSerializer):
    """Kompakte Liste für Übersicht"""
    status_display = serializers.ReadOnlyField()
    total_nodes = serializers.ReadOnlyField()
    running_nodes_count = serializers.ReadOnlyField()
    is_running = serializers.ReadOnlyField()
    
    class Meta:
        model = TorNetwork
        fields = [
            'id', 'name', 'slug', 'description',
            'template', 'status', 'status_display',
            'total_nodes', 'running_nodes_count', 'is_running',
            'consensus_valid', 'bootstrap_progress',
            'capture_enabled', 'created_at', 'started_at',
        ]


class TorNetworkDetailSerializer(serializers.ModelSerializer):
    """Vollständige Details"""
    status_display = serializers.ReadOnlyField()
    total_nodes = serializers.ReadOnlyField()
    running_nodes_count = serializers.ReadOnlyField()
    is_running = serializers.ReadOnlyField()
    nodes = serializers.SerializerMethodField()
    
    class Meta:
        model = TorNetwork
        fields = '__all__'
        read_only_fields = [
            'id', 'slug', 'docker_network_name', 'container_prefix',
            'status', 'status_message', 'bootstrap_progress',
            'consensus_valid', 'consensus_valid_after', 
            'consensus_fresh_until', 'consensus_valid_until',
            'total_circuits_created', 'total_bytes_transferred', 'total_cells_processed',
            'created_at', 'updated_at', 'started_at', 'stopped_at',
        ]
    
    def get_nodes(self, obj):
        """Nodes gruppiert nach Typ"""
        nodes = obj.nodes.all()
        return TorNodeListSerializer(nodes, many=True).data


class TorNetworkCreateSerializer(serializers.ModelSerializer):
    """Für Network-Erstellung"""
    
    class Meta:
        model = TorNetwork
        fields = [
            'name', 'description', 'template',
            'num_directory_authorities', 'num_guard_relays',
            'num_middle_relays', 'num_exit_relays',
            'num_clients', 'num_hidden_services',
            'base_control_port', 'base_socks_port',
            'base_or_port', 'base_dir_port',
            'testing_tor_network', 'voting_interval', 'assume_reachable',
            'capture_enabled', 'capture_filter',
            'max_capture_size_mb', 'capture_rotate_interval',
        ]
    
    def validate_name(self, value):
        """Prüft ob Name eindeutig ist"""
        if self.instance:
            exists = TorNetwork.objects.filter(name=value).exclude(pk=self.instance.pk).exists()
        else:
            exists = TorNetwork.objects.filter(name=value).exists()
        
        if exists:
            raise serializers.ValidationError(f'Network "{value}" exists already.')
        return value


# =============================================================================
# TorNode Serializers
# =============================================================================

class TorNodeListSerializer(serializers.ModelSerializer):
    """Kompakte Node-Liste"""
    status_display = serializers.ReadOnlyField()
    node_type_icon = serializers.ReadOnlyField()
    is_running = serializers.ReadOnlyField()
    total_bandwidth = serializers.ReadOnlyField()
    
    class Meta:
        model = TorNode
        fields = [
            'id', 'name', 'node_type', 'node_type_icon', 'index',
            'status', 'status_display', 'is_running',
            'control_port', 'socks_port', 'or_port', 'dir_port',
            'fingerprint', 'nickname', 'onion_address',
            'bytes_read', 'bytes_written', 'total_bandwidth',
            'circuits_active', 'bootstrap_progress',
            'capture_enabled', 'started_at',
        ]


class TorNodeDetailSerializer(serializers.ModelSerializer):
    """Vollständige Node-Details"""
    status_display = serializers.ReadOnlyField()
    node_type_icon = serializers.ReadOnlyField()
    is_running = serializers.ReadOnlyField()
    is_relay = serializers.ReadOnlyField()
    total_bandwidth = serializers.ReadOnlyField()
    network_name = serializers.CharField(source='network.name', read_only=True)
    captures = serializers.SerializerMethodField()
    
    class Meta:
        model = TorNode
        fields = '__all__'
        read_only_fields = [
            'id', 'container_id', 'container_name',
            'fingerprint', 'v3_identity', 'onion_address', 'flags',
            'status', 'status_message', 'bootstrap_progress',
            'bytes_read', 'bytes_written', 'circuits_created', 'circuits_active',
            'bandwidth_rate', 'bandwidth_burst',
            'created_at', 'updated_at', 'started_at', 'last_seen',
        ]
    
    def get_captures(self, obj):
        """Letzte Captures des Nodes"""
        captures = obj.captures.all()[:5]
        return TrafficCaptureListSerializer(captures, many=True).data


# =============================================================================
# TrafficCapture Serializers
# =============================================================================

class TrafficCaptureListSerializer(serializers.ModelSerializer):
    """Kompakte Capture-Liste"""
    status_display = serializers.ReadOnlyField()
    file_size_mb = serializers.ReadOnlyField()
    packets_per_second = serializers.ReadOnlyField()
    is_recording = serializers.ReadOnlyField()
    node_name = serializers.CharField(source='node.name', read_only=True)
    
    class Meta:
        model = TrafficCapture
        fields = [
            'id', 'name', 'node', 'node_name',
            'capture_type', 'status', 'status_display',
            'file_path', 'file_size_mb', 'is_recording',
            'started_at', 'stopped_at', 'duration_seconds',
            'packet_count', 'packets_per_second',
            'unique_flows', 'tor_cells_detected',
        ]


class TrafficCaptureDetailSerializer(serializers.ModelSerializer):
    """Vollständige Capture-Details"""
    status_display = serializers.ReadOnlyField()
    file_size_mb = serializers.ReadOnlyField()
    packets_per_second = serializers.ReadOnlyField()
    is_recording = serializers.ReadOnlyField()
    node_name = serializers.CharField(source='node.name', read_only=True)
    network_name = serializers.CharField(source='node.network.name', read_only=True)
    
    class Meta:
        model = TrafficCapture
        fields = '__all__'
        read_only_fields = [
            'id', 'file_size_bytes', 'file_hash_sha256',
            'packet_count', 'bytes_captured', 'packets_dropped',
            'unique_flows', 'tor_cells_detected',
            'first_packet_time', 'last_packet_time', 'avg_inter_packet_delay_ms',
            'created_at', 'updated_at',
        ]


# =============================================================================
# CircuitEvent Serializers
# =============================================================================

class CircuitEventSerializer(serializers.ModelSerializer):
    """Circuit Event Details"""
    path_display = serializers.ReadOnlyField()
    source_node_name = serializers.CharField(source='source_node.name', read_only=True)
    
    class Meta:
        model = CircuitEvent
        fields = [
            'id', 'circuit_id', 'event_type', 'purpose',
            'path', 'path_display', 'path_length',
            'status', 'reason', 'remote_reason',
            'event_time', 'build_time_ms',
            'source_node', 'source_node_name',
            'created_at',
        ]


# =============================================================================
# Action Serializers
# =============================================================================

class NetworkActionSerializer(serializers.Serializer):
    """Serializer für Netzwerk-Aktionen"""
    action = serializers.ChoiceField(
        choices=['create', 'start', 'stop', 'restart', 'delete'],
        help_text='Network action to perform'
    )
    remove_volumes = serializers.BooleanField(
        default=False,
        required=False,
        help_text='Also remove data volumes (only for delete action)'
    )


class NodeActionSerializer(serializers.Serializer):
    """Serializer für Node-Aktionen"""
    action = serializers.ChoiceField(
        choices=['start', 'stop', 'restart', 'delete'],
        help_text='Node action to perform'
    )
    remove_volumes = serializers.BooleanField(
        default=False,
        required=False,
        help_text='Also remove data volumes (only for delete action)'
    )


class CaptureActionSerializer(serializers.Serializer):
    """Serializer für Capture-Aktionen"""
    action = serializers.ChoiceField(
        choices=['start', 'stop', 'analyze', 'delete'],
        help_text='Capture action to perform'
    )
    filter_expression = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='BPF filter expression (for start action)'
    )