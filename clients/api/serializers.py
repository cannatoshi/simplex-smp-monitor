"""
Serializers für SimpleX CLI Clients API
"""

from rest_framework import serializers
from clients.models import SimplexClient, ClientConnection, TestMessage


class SimplexClientListSerializer(serializers.ModelSerializer):
    """Serializer für Client-Liste"""
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
    """Serializer für Client-Details"""
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
    """Serializer für Client-Erstellung/Update"""
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


class ClientConnectionSerializer(serializers.ModelSerializer):
    """Serializer für Client-Verbindungen"""
    client_a_name = serializers.CharField(source='client_a.name', read_only=True)
    client_b_name = serializers.CharField(source='client_b.name', read_only=True)
    client_a_slug = serializers.CharField(source='client_a.slug', read_only=True)
    client_b_slug = serializers.CharField(source='client_b.slug', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ClientConnection
        fields = [
            'id', 'client_a', 'client_b',
            'client_a_name', 'client_b_name',
            'client_a_slug', 'client_b_slug',
            'contact_name_on_a', 'contact_name_on_b',
            'status', 'status_display',
            'created_at', 'connected_at'
        ]


class TestMessageSerializer(serializers.ModelSerializer):
    """Serializer für Test-Nachrichten"""
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    status_display = serializers.CharField(source='get_delivery_status_display', read_only=True)
    
    class Meta:
        model = TestMessage
        fields = [
            'id', 'sender', 'recipient',
            'sender_name', 'recipient_name',
            'content', 'delivery_status', 'status_display',
            'total_latency_ms', 'created_at'
        ]


class ClientStatsSerializer(serializers.Serializer):
    """Serializer für Client-Statistiken"""
    total = serializers.IntegerField()
    running = serializers.IntegerField()
    stopped = serializers.IntegerField()
    error = serializers.IntegerField()
    total_messages_sent = serializers.IntegerField()
    total_messages_received = serializers.IntegerField()
    available_ports = serializers.ListField(child=serializers.IntegerField())
