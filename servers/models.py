from django.db import models
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
    """SMP/XFTP Server Configuration"""
    SERVER_TYPES = [('smp', 'SMP'), ('xftp', 'XFTP')]
    STATUS_CHOICES = [
        ('unknown', 'Unknown'),
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]

    # === Basic Info ===
    name = models.CharField(max_length=100)
    server_type = models.CharField(max_length=10, choices=SERVER_TYPES, default='smp')
    address = models.TextField(help_text="Full smp://... or xftp://... URL")
    description = models.TextField(blank=True, help_text="Notes about this server")
    location = models.CharField(max_length=100, blank=True, help_text="Physical location")
    
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
        return f"{self.name} ({self.server_type.upper()})"

    def _parse_address(self):
        pattern = r'^(smp|xftp)://([^:@]+)(?::([^@]+))?@(.+)$'
        match = re.match(pattern, self.address.strip())
        if match:
            return {
                'protocol': match.group(1),
                'fingerprint': match.group(2),
                'password': match.group(3) or '',
                'host': match.group(4)
            }
        return None

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
        return parsed['host'] if parsed else self.address

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
