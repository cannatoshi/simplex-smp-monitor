"""
Servers API - Serializers

Extended with Docker hosting support (v0.1.12)
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
    
    # Docker fields
    is_docker_running = serializers.ReadOnlyField()
    docker_status_display = serializers.ReadOnlyField()
    effective_address = serializers.ReadOnlyField()
    hosting_mode_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Server
        fields = [
            'id', 'name', 'server_type', 'host', 'fingerprint', 'password',
            'is_active', 'maintenance_mode', 'last_status', 
            'last_latency', 'last_check', 'is_onion',
            'uptime_percent', 'categories', 'sort_order',
            'location', 'description', 'address',
            # Docker fields
            'is_docker_hosted', 'docker_status', 'is_docker_running',
            'docker_status_display', 'exposed_port', 'effective_address',
            'generated_address',
            # Hosting mode fields (NEW)
            'hosting_mode', 'hosting_mode_display', 'host_ip', 'onion_address',
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
    
    # Docker fields (read-only computed)
    is_docker_running = serializers.ReadOnlyField()
    docker_status_display = serializers.ReadOnlyField()
    docker_image_name = serializers.ReadOnlyField()
    default_internal_port = serializers.ReadOnlyField()
    effective_address = serializers.ReadOnlyField()
    
    # Hosting mode fields (NEW)
    is_tor_hosted = serializers.ReadOnlyField()
    hosting_mode_display = serializers.ReadOnlyField()
    effective_host = serializers.ReadOnlyField()
    
    class Meta:
        model = Server
        fields = '__all__'
        read_only_fields = [
            'total_checks', 'successful_checks', 'avg_latency',
            'last_check', 'last_status', 'last_latency', 'last_error',
            'created_at', 'updated_at',
            # Docker auto-generated fields
            'container_id', 'container_name', 'data_volume', 'config_volume',
            'generated_fingerprint', 'generated_address', 'onion_address',
        ]


class ServerCreateUpdateSerializer(serializers.ModelSerializer):
    """Für Create/Update Operations - mit Docker Support"""
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
            # Basic
            'id', 'name', 'server_type', 'address', 'description', 'location',
            'is_active', 'maintenance_mode', 'custom_timeout', 'priority',
            'expected_uptime', 'max_latency', 'category_ids', 'sort_order',
            
            # Docker hosting (NEW)
            'is_docker_hosted', 'exposed_port',
            'hosting_mode', 'host_ip',  # NEW: Hosting mode fields
            
            # SSH
            'ssh_host', 'ssh_port', 'ssh_user', 'ssh_key_path',
            
            # Control Port
            'control_port_enabled', 'control_port', 
            'control_port_admin_password', 'control_port_user_password',
            
            # Telegraf
            'telegraf_enabled', 'telegraf_interval',
            'influxdb_url', 'influxdb_token', 'influxdb_org', 'influxdb_bucket',
            
            # Paths
            'simplex_config_path', 'simplex_data_path', 'simplex_stats_file',
        ]
    
    def validate_name(self, value):
        """
        Check that server name is unique (except for the current instance on update)
        """
        # For updates, exclude the current instance from the check
        if self.instance:
            exists = Server.objects.filter(name=value).exclude(pk=self.instance.pk).exists()
        else:
            exists = Server.objects.filter(name=value).exists()
        
        if exists:
            raise serializers.ValidationError(f'A server with name "{value}" already exists.')
        
        return value
    
    def validate(self, data):
        """
        Validate that either address is provided (external) or is_docker_hosted is True
        """
        is_docker = data.get('is_docker_hosted', False)
        address = data.get('address', '')
        
        # For updates, check existing values if not in data
        if self.instance:
            if 'is_docker_hosted' not in data:
                is_docker = self.instance.is_docker_hosted
            if 'address' not in data:
                address = self.instance.address
        
        if not is_docker and not address:
            raise serializers.ValidationError({
                'address': 'Address is required for external servers'
            })
        
        return data


class ServerDockerActionSerializer(serializers.Serializer):
    """Serializer für Docker Container Aktionen"""
    action = serializers.ChoiceField(
        choices=['start', 'stop', 'restart', 'delete'],
        help_text='Docker container action to perform'
    )
    remove_volumes = serializers.BooleanField(
        default=False,
        required=False,
        help_text='Also remove data volumes (only for delete action)'
    )


class ServerLogsSerializer(serializers.Serializer):
    """Serializer für Container Logs Anfrage"""
    tail = serializers.IntegerField(
        default=100,
        min_value=1,
        max_value=10000,
        help_text='Number of log lines to return'
    )
    timestamps = serializers.BooleanField(
        default=True,
        help_text='Include timestamps in log output'
    )


class ServerLogsResponseSerializer(serializers.Serializer):
    """Response Serializer für Container Logs"""
    logs = serializers.CharField()
    container_name = serializers.CharField()
    container_status = serializers.CharField()


class DockerImageModeSerializer(serializers.Serializer):
    """Status für IP und Tor Mode eines Server-Typs"""
    ip = serializers.BooleanField()
    tor = serializers.BooleanField()


class DockerImagesStatusSerializer(serializers.Serializer):
    """Response Serializer für Docker Images Status"""
    smp = DockerImageModeSerializer()
    xftp = DockerImageModeSerializer()
    ntf = DockerImageModeSerializer()