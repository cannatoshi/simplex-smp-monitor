"""
Servers API - Serializers
"""
from rest_framework import serializers
from servers.models import Server, Category


class CategorySerializer(serializers.ModelSerializer):
    server_count = serializers.ReadOnlyField()
    online_server_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'color', 'icon', 
            'sort_order', 'server_count', 'online_server_count',
            'created_at', 'updated_at'
        ]


class ServerListSerializer(serializers.ModelSerializer):
    """Kompakte Server-Liste für Übersichten"""
    fingerprint = serializers.ReadOnlyField()
    password = serializers.ReadOnlyField()
    host = serializers.ReadOnlyField()
    is_onion = serializers.ReadOnlyField()
    uptime_percent = serializers.ReadOnlyField()
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Server
        fields = [
            'id', 'name', 'server_type', 'host', 'fingerprint', 'password',
            'is_active', 'maintenance_mode', 'last_status', 
            'last_latency', 'last_check', 'is_onion',
            'uptime_percent', 'categories', 'sort_order',
            'location', 'description', 'address'  # ADDED
        ]


class ServerDetailSerializer(serializers.ModelSerializer):
    """Vollständige Server-Details"""
    fingerprint = serializers.ReadOnlyField()
    password = serializers.ReadOnlyField()
    host = serializers.ReadOnlyField()
    is_onion = serializers.ReadOnlyField()
    effective_timeout = serializers.ReadOnlyField()
    uptime_percent = serializers.ReadOnlyField()
    is_below_sla = serializers.ReadOnlyField()
    ssh_configured = serializers.ReadOnlyField()
    control_port_configured = serializers.ReadOnlyField()
    telegraf_configured = serializers.ReadOnlyField()
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        source='categories',
        required=False
    )
    
    class Meta:
        model = Server
        fields = '__all__'
        read_only_fields = [
            'total_checks', 'successful_checks', 'avg_latency',
            'last_check', 'last_status', 'last_latency', 'last_error',
            'created_at', 'updated_at'
        ]


class ServerCreateUpdateSerializer(serializers.ModelSerializer):
    """Für Create/Update Operations"""
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        source='categories',
        required=False
    )
    
    class Meta:
        model = Server
        fields = [
            'id', 'name', 'server_type', 'address', 'description', 'location',
            'is_active', 'maintenance_mode', 'custom_timeout', 'priority',
            'expected_uptime', 'max_latency', 'category_ids', 'sort_order',
            'ssh_host', 'ssh_port', 'ssh_user', 'ssh_key_path',
            'control_port_enabled', 'control_port', 
            'control_port_admin_password', 'control_port_user_password',
            'telegraf_enabled', 'telegraf_interval',
            'influxdb_url', 'influxdb_token', 'influxdb_org', 'influxdb_bucket',
            'simplex_config_path', 'simplex_data_path', 'simplex_stats_file',
        ]
