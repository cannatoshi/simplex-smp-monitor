"""
Stresstests API - Serializers
"""
from rest_framework import serializers
from stresstests.models import Test, TestResult, Metric
from servers.models import Server
from servers.api.serializers import ServerListSerializer


class TestListSerializer(serializers.ModelSerializer):
    """Kompakte Test-Liste"""
    success_rate = serializers.ReadOnlyField()
    delivery_rate = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    server_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = [
            'id', 'name', 'test_type', 'status', 'description',
            'total_runs', 'successful_runs', 'failed_runs',
            'success_rate', 'delivery_rate', 'is_active',
            'last_run', 'created_at', 'server_count'
        ]
    
    def get_server_count(self, obj):
        if obj.test_all_active_servers:
            return Server.objects.filter(is_active=True, maintenance_mode=False).count()
        return obj.servers.count()


class TestDetailSerializer(serializers.ModelSerializer):
    """Vollständige Test-Details"""
    success_rate = serializers.ReadOnlyField()
    delivery_rate = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    servers = ServerListSerializer(many=True, read_only=True)
    server_ids = serializers.PrimaryKeyRelatedField(
        queryset=Server.objects.all(),
        many=True,
        write_only=True,
        source='servers',
        required=False
    )
    
    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = [
            'total_runs', 'successful_runs', 'failed_runs',
            'messages_sent', 'messages_received',
            'avg_latency_ms', 'min_latency_ms', 'max_latency_ms',
            'created_at', 'updated_at', 'started_at', 'last_run'
        ]


class TestResultSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'test', 'server', 'server_name', 'timestamp',
            'success', 'latency_ms', 'error_message',
            'used_tor', 'tls_version'
        ]


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = '__all__'
