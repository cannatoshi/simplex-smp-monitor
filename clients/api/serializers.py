"""
SimpleX SMP Monitor by cannatoshi
GitHub: https://github.com/cannatoshi/simplex-smp-monitor
Licensed under AGPL-3.0

Serializers for SimpleX CLI Clients API

Contains serializers for:
- SimplexClient (list, detail, create/update)
- ClientConnection
- TestMessage (with direction and profile support)
- LatencyHistory (for modal with pagination)
- LatencyStats (for graphs and statistics)
- ClientStats (global statistics)
"""

from rest_framework import serializers
from clients.models import SimplexClient, ClientConnection, TestMessage, ClientTestRun as TestRun


# =============================================================================
# CLIENT SERIALIZERS
# =============================================================================

class SimplexClientListSerializer(serializers.ModelSerializer):
    """Serializer for client list view - compact overview"""
    connection_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    uptime_display = serializers.CharField(read_only=True)
    delivery_success_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = SimplexClient
        fields = [
            'id', 'name', 'slug', 'profile_name', 'description',
            'websocket_port', 'status', 'status_display',
            'use_tor', 'messages_sent', 'messages_received', 'messages_failed',
            'connection_count', 'uptime_display', 'delivery_success_rate',
            'created_at', 'last_active_at', 'started_at'
        ]
    
    def get_connection_count(self, obj):
        return obj.connections_as_a.count() + obj.connections_as_b.count()


class SimplexClientDetailSerializer(serializers.ModelSerializer):
    """Serializer for client detail view - full information including latency stats"""
    connection_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    uptime_display = serializers.CharField(read_only=True)
    delivery_success_rate = serializers.FloatField(read_only=True)
    avg_latency_ms = serializers.FloatField(read_only=True)
    min_latency_ms = serializers.IntegerField(read_only=True)
    max_latency_ms = serializers.IntegerField(read_only=True)
    messages_delivered = serializers.IntegerField(read_only=True)
    smp_server_ids = serializers.PrimaryKeyRelatedField(
        source='smp_servers', many=True, read_only=True
    )
    
    class Meta:
        model = SimplexClient
        fields = [
            'id', 'name', 'slug', 'profile_name', 'description',
            'container_id', 'container_name', 'websocket_port', 'data_volume',
            'status', 'status_display', 'last_error',
            'use_tor', 'smp_server_ids',
            'messages_sent', 'messages_received', 'messages_failed', 'messages_delivered',
            'connection_count', 'uptime_display', 'delivery_success_rate',
            'avg_latency_ms', 'min_latency_ms', 'max_latency_ms',
            'created_at', 'updated_at', 'started_at', 'last_active_at'
        ]
    
    def get_connection_count(self, obj):
        return obj.connections_as_a.count() + obj.connections_as_b.count()


class SimplexClientCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for client creation and updates"""
    smp_server_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = SimplexClient
        fields = [
            'name', 'slug', 'profile_name', 'description',
            'websocket_port', 'use_tor', 'smp_server_ids'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'slug': {'required': False},
            'profile_name': {'required': False},
        }
    
    def create(self, validated_data):
        smp_server_ids = validated_data.pop('smp_server_ids', [])
        client = SimplexClient.objects.create(**validated_data)
        if smp_server_ids:
            client.smp_servers.set(smp_server_ids)
        return client
    
    def update(self, instance, validated_data):
        smp_server_ids = validated_data.pop('smp_server_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if smp_server_ids is not None:
            instance.smp_servers.set(smp_server_ids)
        return instance


# =============================================================================
# CONNECTION SERIALIZERS
# =============================================================================

class ClientConnectionSerializer(serializers.ModelSerializer):
    """Serializer for client connections with profile names"""
    client_a_name = serializers.CharField(source='client_a.name', read_only=True)
    client_b_name = serializers.CharField(source='client_b.name', read_only=True)
    client_a_slug = serializers.CharField(source='client_a.slug', read_only=True)
    client_b_slug = serializers.CharField(source='client_b.slug', read_only=True)
    # NEW: Profile names (nicknames like "maria", "bob")
    client_a_profile = serializers.CharField(source='client_a.profile_name', read_only=True)
    client_b_profile = serializers.CharField(source='client_b.profile_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ClientConnection
        fields = [
            'id', 'client_a', 'client_b',
            'client_a_name', 'client_b_name',
            'client_a_slug', 'client_b_slug',
            'client_a_profile', 'client_b_profile',
            'contact_name_on_a', 'contact_name_on_b',
            'status', 'status_display',
            'created_at', 'connected_at'
        ]


# =============================================================================
# MESSAGE SERIALIZERS
# =============================================================================

class TestMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for test messages with direction and profile support.
    
    Used for the messages table in client detail view.
    Includes sender/recipient profiles and message direction detection.
    """
    # Basic info
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    status_display = serializers.CharField(source='get_delivery_status_display', read_only=True)
    
    # NEW: Profile names (nicknames)
    sender_profile = serializers.CharField(source='sender.profile_name', read_only=True)
    recipient_profile = serializers.CharField(source='recipient.profile_name', read_only=True)
    
    # NEW: Clean content without tracking ID prefix
    content_clean = serializers.CharField(source='content_without_tracking', read_only=True)
    
    # NEW: Tracking ID for reliable message matching
    tracking_id = serializers.CharField(read_only=True)
    
    # NEW: Message direction (sent/received) based on context
    direction = serializers.SerializerMethodField()
    
    class Meta:
        model = TestMessage
        fields = [
            'id', 'sender', 'recipient',
            'sender_name', 'recipient_name',
            'sender_profile', 'recipient_profile',
            'content', 'content_clean',
            'delivery_status', 'status_display',
            'total_latency_ms', 'latency_to_server_ms', 'latency_to_client_ms',
            'tracking_id', 'direction',
            'sent_at', 'client_received_at',
            'created_at'
        ]
    
    def get_direction(self, obj):
        """
        Determine message direction based on request context.
        
        Checks:
        1. Explicit 'direction' query param
        2. 'client' query param to determine if message was sent or received
        """
        request = self.context.get('request')
        if request:
            # Check explicit direction param
            direction = request.query_params.get('direction')
            if direction in ['sent', 'received']:
                return direction
            
            # Determine from client param
            client_id = request.query_params.get('client')
            if client_id:
                if str(obj.sender_id) == client_id:
                    return 'sent'
                elif str(obj.recipient_id) == client_id:
                    return 'received'
        
        return 'sent'  # Default


# =============================================================================
# LATENCY SERIALIZERS (for Modal and Graphs)
# =============================================================================

class LatencyHistorySerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Latency History Modal.
    
    Includes all information needed for the paginated table:
    - Sender/Recipient with name, profile, and slug
    - Content preview (first 30 chars without tracking ID)
    - Latency with color indicator
    - All relevant timestamps
    """
    # Sender info
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    sender_profile = serializers.CharField(source='sender.profile_name', read_only=True)
    sender_slug = serializers.CharField(source='sender.slug', read_only=True)
    
    # Recipient info
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    recipient_profile = serializers.CharField(source='recipient.profile_name', read_only=True)
    recipient_slug = serializers.CharField(source='recipient.slug', read_only=True)
    
    # Content preview (truncated, without tracking ID)
    content_preview = serializers.SerializerMethodField()
    
    # Status
    status_display = serializers.CharField(source='get_delivery_status_display', read_only=True)
    
    # Latency color indicator for visual feedback
    latency_indicator = serializers.SerializerMethodField()
    
    class Meta:
        model = TestMessage
        fields = [
            'id', 'tracking_id',
            'sender', 'recipient',
            'sender_name', 'recipient_name',
            'sender_profile', 'recipient_profile',
            'sender_slug', 'recipient_slug',
            'content_preview',
            'delivery_status', 'status_display',
            'total_latency_ms', 'latency_to_server_ms', 'latency_to_client_ms',
            'sent_at', 'client_received_at',
            'latency_indicator',
            'created_at'
        ]
    
    def get_content_preview(self, obj):
        """First 30 characters of content without tracking ID prefix"""
        clean_content = obj.content_without_tracking
        if len(clean_content) > 30:
            return clean_content[:30] + '...'
        return clean_content
    
    def get_latency_indicator(self, obj):
        """
        Color indicator based on latency thresholds:
        - green: < 500ms (fast)
        - yellow: 500ms - 2000ms (moderate)
        - red: >= 2000ms (slow)
        - gray: no data
        """
        if obj.total_latency_ms is None:
            return 'gray'
        if obj.total_latency_ms < 500:
            return 'green'
        elif obj.total_latency_ms < 2000:
            return 'yellow'
        return 'red'


class LatencyStatsSerializer(serializers.Serializer):
    """
    Serializer for latency statistics and graph data.
    
    Used by the latency-stats endpoint to provide:
    - Aggregate statistics (avg, min, max)
    - Message counts by status
    - Time series data for the graph
    """
    # Aggregate stats
    avg_latency = serializers.FloatField()
    min_latency = serializers.IntegerField(allow_null=True)
    max_latency = serializers.IntegerField(allow_null=True)
    
    # Message counts
    total_messages = serializers.IntegerField()
    delivered_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    
    # Time series data for graph (list of {timestamp, latency, ...})
    time_series = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    
    # Selected time range
    time_range = serializers.CharField()


class LatencyGraphPointSerializer(serializers.Serializer):
    """Single data point for the latency graph"""
    timestamp = serializers.DateTimeField()
    latency = serializers.IntegerField()
    message_id = serializers.UUIDField()
    sender_profile = serializers.CharField()
    recipient_profile = serializers.CharField()


# =============================================================================
# STATISTICS SERIALIZERS
# =============================================================================

class ClientStatsSerializer(serializers.Serializer):
    """Serializer for global client statistics (dashboard overview)"""
    total = serializers.IntegerField()
    running = serializers.IntegerField()
    stopped = serializers.IntegerField()
    error = serializers.IntegerField()
    total_messages_sent = serializers.IntegerField()
    total_messages_received = serializers.IntegerField()
    available_ports = serializers.ListField(child=serializers.IntegerField())


class ResetResponseSerializer(serializers.Serializer):
    """Serializer for reset action responses"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    deleted_count = serializers.IntegerField(required=False)
    reset_values = serializers.DictField(required=False)


# =============================================================================
# TEST RUN SERIALIZERS
# =============================================================================

class TestRunSerializer(serializers.ModelSerializer):
    """Serializer for TestRun - full details with extended latency metrics"""
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    sender_profile = serializers.CharField(source='sender.profile_name', read_only=True)
    sender_use_tor = serializers.BooleanField(source='sender.use_tor', read_only=True)
    progress_percent = serializers.FloatField(read_only=True)
    duration_seconds = serializers.FloatField(read_only=True)
    
    # Extended latency fields
    avg_latency_to_server_ms = serializers.FloatField(read_only=True)
    min_latency_to_server_ms = serializers.IntegerField(read_only=True)
    max_latency_to_server_ms = serializers.IntegerField(read_only=True)
    avg_latency_to_client_ms = serializers.FloatField(read_only=True)
    min_latency_to_client_ms = serializers.IntegerField(read_only=True)
    max_latency_to_client_ms = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TestRun
        fields = [
            'id', 'name', 'sender', 'sender_name', 'sender_profile', 'sender_use_tor',
            'message_count', 'interval_ms', 'message_size', 'recipient_mode',
            'status', 'messages_sent', 'messages_delivered', 'messages_failed',
            # Total latency
            'avg_latency_ms', 'min_latency_ms', 'max_latency_ms',
            # To Server latency
            'avg_latency_to_server_ms', 'min_latency_to_server_ms', 'max_latency_to_server_ms',
            # To Client latency
            'avg_latency_to_client_ms', 'min_latency_to_client_ms', 'max_latency_to_client_ms',
            # Other fields
            'success_rate', 'progress_percent', 'duration_seconds',
            'created_at', 'started_at', 'completed_at',
        ]
        read_only_fields = [
            'id', 'status', 'messages_sent', 'messages_delivered', 'messages_failed',
            'avg_latency_ms', 'min_latency_ms', 'max_latency_ms',
            'avg_latency_to_server_ms', 'min_latency_to_server_ms', 'max_latency_to_server_ms',
            'avg_latency_to_client_ms', 'min_latency_to_client_ms', 'max_latency_to_client_ms',
            'created_at', 'started_at', 'completed_at',
        ]


class TestRunCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new TestRun"""
    selected_recipients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SimplexClient.objects.all(),
        required=False
    )
    
    class Meta:
        model = TestRun
        fields = [
            'name', 'sender', 'message_count', 'interval_ms',
            'message_size', 'recipient_mode', 'selected_recipients',
        ]
    
    def validate(self, data):
        """Validate test run configuration"""
        sender = data.get('sender')
        
        if sender and sender.status != 'running':
            raise serializers.ValidationError({
                'sender': f'Sender client must be running (current: {sender.status})'
            })
        
        recipient_mode = data.get('recipient_mode', 'round_robin')
        selected = data.get('selected_recipients', [])
        
        if recipient_mode == 'selected' and not selected:
            raise serializers.ValidationError({
                'selected_recipients': 'At least one recipient must be selected'
            })
        
        return data


class TestRunMessageSerializer(serializers.ModelSerializer):
    """Serializer for test messages within a test run"""
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    
    class Meta:
        model = TestMessage
        fields = [
            'id', 'tracking_id', 'sender_name', 'recipient_name',
            'delivery_status', 'sent_at', 'server_received_at', 'client_received_at',
            'latency_to_server_ms', 'latency_to_client_ms', 'total_latency_ms',
            'error_message',
        ]