from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import re


class Category(models.Model):
    """Server Category for organizing servers"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    color = models.CharField(max_length=7, default='#0ea5e9')
    icon = models.CharField(max_length=50, default='folder')
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    @property
    def server_count(self):
        return self.servers.count()

    @property
    def active_server_count(self):
        return self.servers.filter(is_active=True).count()

    @property
    def online_server_count(self):
        return self.servers.filter(last_status='online').count()


class Server(models.Model):
    """SMP/XFTP Server Configuration - supports both external and Docker-hosted servers"""
    
    SERVER_TYPES = [('smp', 'SMP'), ('xftp', 'XFTP'), ('ntf', 'NTF')]
    STATUS_CHOICES = [
        ('unknown', 'Unknown'),
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]
    
    # === Docker Status Choices (analog zu SimplexClient) ===
    class DockerStatus(models.TextChoices):
        NOT_CREATED = 'not_created', 'Not Created'
        CREATED = 'created', 'Created'
        STARTING = 'starting', 'Starting...'
        RUNNING = 'running', 'Running'
        STOPPING = 'stopping', 'Stopping...'
        STOPPED = 'stopped', 'Stopped'
        ERROR = 'error', 'Error'

    # === Basic Info ===
    name = models.CharField(max_length=100)
    server_type = models.CharField(max_length=10, choices=SERVER_TYPES, default='smp')
    address = models.TextField(
        blank=True,  # CHANGED: Now optional for Docker-hosted servers
        help_text="Full smp://... or xftp://... URL (auto-generated for Docker servers)"
    )
    description = models.TextField(blank=True, help_text="Notes about this server")
    location = models.CharField(max_length=100, blank=True, help_text="Physical location")
    
    # ==========================================================================
    # NEW: Docker Hosting Configuration
    # ==========================================================================
    is_docker_hosted = models.BooleanField(
        default=False,
        verbose_name='Docker Hosted',
        help_text='Run this server locally in a Docker container'
    )
    
    # Hosting Mode (IP or Tor)
    class HostingMode(models.TextChoices):
        IP = 'ip', 'IP Address (LAN)'
        TOR = 'tor', 'Tor Hidden Service (.onion)'
    
    hosting_mode = models.CharField(
        max_length=10,
        choices=HostingMode.choices,
        default=HostingMode.IP,
        verbose_name='Hosting Mode',
        help_text='How the server should be accessible'
    )
    
    # For IP mode - which IP to bind/advertise
    host_ip = models.CharField(
        max_length=45,  # IPv6 max length
        blank=True,
        default='0.0.0.0',
        verbose_name='Host IP',
        help_text='IP address for server certificate (use host IP for LAN access)'
    )
    
    # For Tor mode - generated .onion address
    onion_address = models.CharField(
        max_length=62,  # v3 onion = 56 chars + .onion
        blank=True,
        verbose_name='Onion Address',
        help_text='Tor hidden service address (auto-generated)'
    )
    
    # Docker Container Info
    container_id = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='Container ID',
        help_text='Docker container ID (set automatically)'
    )
    container_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Container Name',
        help_text='Docker container name (generated automatically)'
    )
    data_volume = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Data Volume',
        help_text='Docker volume for persistent data'
    )
    config_volume = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Config Volume',
        help_text='Docker volume for configuration'
    )
    
    # Docker Port Mapping
    exposed_port = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1024), MaxValueValidator(65535)],
        verbose_name='Exposed Port',
        help_text='Host port for Docker container (5223 for SMP, 443 for XFTP/NTF)'
    )
    
    # Docker Status
    docker_status = models.CharField(
        max_length=20,
        choices=DockerStatus.choices,
        default=DockerStatus.NOT_CREATED,
        verbose_name='Docker Status'
    )
    docker_error = models.TextField(
        blank=True,
        verbose_name='Docker Error',
        help_text='Last Docker error message'
    )
    
    # Server Fingerprint (extracted from container logs after init)
    generated_fingerprint = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Generated Fingerprint',
        help_text='Server fingerprint (extracted after container initialization)'
    )
    generated_address = models.TextField(
        blank=True,
        verbose_name='Generated Address',
        help_text='Full server address (generated after container initialization)'
    )
    
    # ==========================================================================
    # END: Docker Hosting Configuration
    # ==========================================================================
    
    # === Status & Monitoring ===
    is_active = models.BooleanField(default=True, help_text="Include in tests")
    maintenance_mode = models.BooleanField(default=False, help_text="Temporarily exclude from tests")
    last_check = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    last_latency = models.IntegerField(null=True, blank=True, help_text="Last latency in ms")
    last_error = models.TextField(blank=True, help_text="Last error message")
    
    # === Test Configuration ===
    custom_timeout = models.IntegerField(null=True, blank=True, help_text="Custom timeout in seconds")
    priority = models.IntegerField(default=5, help_text="Priority 1-10 for load balancing")
    
    # === SLA Targets ===
    expected_uptime = models.IntegerField(default=99, help_text="Expected uptime percentage")
    max_latency = models.IntegerField(default=5000, help_text="Max acceptable latency in ms")
    
    # === Statistics (auto-filled) ===
    total_checks = models.IntegerField(default=0)
    successful_checks = models.IntegerField(default=0)
    avg_latency = models.IntegerField(null=True, blank=True, help_text="Average latency in ms")
    
    # === SSH Access ===
    ssh_host = models.CharField(max_length=255, blank=True, help_text="SSH host")
    ssh_port = models.IntegerField(default=22, help_text="SSH port")
    ssh_user = models.CharField(max_length=100, blank=True, help_text="SSH username")
    ssh_key_path = models.CharField(max_length=500, blank=True, help_text="Path to SSH key")
    
    # === Control Port ===
    control_port_enabled = models.BooleanField(default=False, help_text="Control port available")
    control_port = models.IntegerField(default=5224, help_text="Control port number")
    control_port_admin_password = models.CharField(max_length=100, blank=True, help_text="Admin password")
    control_port_user_password = models.CharField(max_length=100, blank=True, help_text="User password")
    
    # === SimpleX Server Config (read from server) ===
    simplex_version = models.CharField(max_length=50, blank=True)
    simplex_fingerprint = models.CharField(max_length=100, blank=True)
    store_log_enabled = models.BooleanField(default=True)
    restore_messages = models.BooleanField(default=True)
    expire_messages_days = models.IntegerField(default=21)
    log_stats_enabled = models.BooleanField(default=True)
    new_queues_allowed = models.BooleanField(default=True)
    websockets_enabled = models.BooleanField(default=False)
    
    # === Telegraf/InfluxDB ===
    telegraf_enabled = models.BooleanField(default=False, help_text="Enable Telegraf metrics collection")
    telegraf_interval = models.IntegerField(default=10, help_text="Collection interval in seconds")
    influxdb_url = models.CharField(max_length=255, blank=True, default='http://localhost:8086')
    influxdb_token = models.CharField(max_length=255, blank=True, help_text="InfluxDB API token")
    influxdb_org = models.CharField(max_length=100, blank=True, default='simplex')
    influxdb_bucket = models.CharField(max_length=100, blank=True, default='simplex-metrics')
    
    # === Paths on Remote Server ===
    simplex_config_path = models.CharField(max_length=255, default='/etc/opt/simplex', help_text="Config directory")
    simplex_data_path = models.CharField(max_length=255, default='/var/opt/simplex', help_text="Data directory")
    simplex_stats_file = models.CharField(max_length=255, default='/var/opt/simplex/smp-server-stats.daily.log')
    
    # === Organization ===
    categories = models.ManyToManyField(Category, related_name='servers', blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        docker_badge = " 🐳" if self.is_docker_hosted else ""
        return f"{self.name} ({self.server_type.upper()}){docker_badge}"
    
    def save(self, *args, **kwargs):
        # Auto-generate Docker-related names
        if self.is_docker_hosted:
            if not self.container_name:
                # Generate: simplex-smp-servername or simplex-xftp-servername
                safe_name = re.sub(r'[^a-z0-9-]', '-', self.name.lower())
                self.container_name = f"simplex-{self.server_type}-{safe_name}"
            
            if not self.data_volume:
                self.data_volume = f"{self.container_name}-data"
            
            if not self.config_volume:
                self.config_volume = f"{self.container_name}-config"
            
            # Set default ports based on server type
            if not self.exposed_port:
                if self.server_type == 'smp':
                    self.exposed_port = self._get_next_available_port(5223, 5299)
                elif self.server_type == 'xftp':
                    self.exposed_port = self._get_next_available_port(5443, 5499)
                elif self.server_type == 'ntf':
                    self.exposed_port = self._get_next_available_port(5543, 5599)
        
        super().save(*args, **kwargs)
    
    def _get_next_available_port(self, start_port: int, end_port: int) -> int:
        """Find next available port in range"""
        used_ports = set(
            Server.objects.filter(is_docker_hosted=True)
            .exclude(pk=self.pk)
            .values_list('exposed_port', flat=True)
        )
        for port in range(start_port, end_port + 1):
            if port not in used_ports:
                return port
        return start_port  # Fallback

    def _parse_address(self):
        # Use generated_address for Docker servers if available
        addr = self.effective_address
        if not addr:
            return None
        pattern = r'^(smp|xftp|ntf)://([^:@]+)(?::([^@]+))?@(.+)$'
        match = re.match(pattern, addr.strip())
        if match:
            return {
                'protocol': match.group(1),
                'fingerprint': match.group(2),
                'password': match.group(3) or '',
                'host': match.group(4)
            }
        return None

    @property
    def effective_address(self):
        """Returns the actual address to use (generated for Docker, manual for external)"""
        if self.is_docker_hosted and self.generated_address:
            return self.generated_address
        return self.address

    @property
    def fingerprint(self):
        parsed = self._parse_address()
        return parsed['fingerprint'] if parsed else ''

    @property
    def password(self):
        parsed = self._parse_address()
        return parsed['password'] if parsed else ''

    @property
    def host(self):
        parsed = self._parse_address()
        return parsed['host'] if parsed else self.effective_address

    @property
    def is_onion(self):
        return '.onion' in self.host

    @property
    def effective_timeout(self):
        if self.custom_timeout:
            return self.custom_timeout
        return 120 if self.is_onion else 30

    @property
    def uptime_percent(self):
        if self.total_checks == 0:
            return None
        return round((self.successful_checks / self.total_checks) * 100, 2)

    @property
    def is_below_sla(self):
        uptime = self.uptime_percent
        if uptime and uptime < self.expected_uptime:
            return True
        if self.last_latency and self.last_latency > self.max_latency:
            return True
        return False
    
    @property
    def ssh_configured(self):
        return bool(self.ssh_host and self.ssh_user)
    
    @property
    def control_port_configured(self):
        return self.control_port_enabled and (self.control_port_admin_password or self.control_port_user_password)
    
    @property
    def telegraf_configured(self):
        return self.telegraf_enabled and self.influxdb_url and self.influxdb_token
    
    # ==========================================================================
    # NEW: Docker-related properties
    # ==========================================================================
    
    @property
    def is_docker_running(self):
        """Check if Docker container is running"""
        return self.docker_status == self.DockerStatus.RUNNING
    
    @property
    def docker_image_name(self):
        """Get the Docker image name for this server type"""
        images = {
            'smp': 'simplex-smp:latest',
            'xftp': 'simplex-xftp:latest',
            'ntf': 'simplex-ntf:latest',
        }
        return images.get(self.server_type, 'simplex-smp:latest')
    
    @property
    def default_internal_port(self):
        """Get the internal port the server listens on"""
        ports = {
            'smp': 5223,
            'xftp': 443,
            'ntf': 443,
        }
        return ports.get(self.server_type, 5223)
    
    @property
    def docker_status_display(self):
        """Human-readable Docker status with emoji"""
        status_map = {
            'not_created': '⚪ Not Created',
            'created': '🔵 Created',
            'starting': '🟡 Starting...',
            'running': '🟢 Running',
            'stopping': '🟡 Stopping...',
            'stopped': '🔴 Stopped',
            'error': '❌ Error',
        }
        return status_map.get(self.docker_status, '❓ Unknown')
    
    @property
    def is_tor_hosted(self):
        """Check if this is a Tor hidden service"""
        return self.is_docker_hosted and self.hosting_mode == self.HostingMode.TOR
    
    @property
    def effective_host(self):
        """Returns the host to use (onion for Tor, IP for IP-mode)"""
        if self.is_tor_hosted and self.onion_address:
            return self.onion_address
        elif self.host_ip:
            return f"{self.host_ip}:{self.exposed_port or self.default_internal_port}"
        return self.host
    
    @property
    def hosting_mode_display(self):
        """Human-readable hosting mode"""
        if not self.is_docker_hosted:
            return '🌐 External'
        elif self.hosting_mode == self.HostingMode.TOR:
            return '🧅 Tor Hidden Service'
        else:
            return '🏠 LAN (IP)'