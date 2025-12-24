from django.db import models
import re

class Server(models.Model):
    """SMP/XFTP Server Konfiguration"""
    SERVER_TYPES = [('smp', 'SMP'), ('xftp', 'XFTP')]
    STATUS_CHOICES = [
        ('unknown', 'Unknown'),
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=100)
    server_type = models.CharField(max_length=10, choices=SERVER_TYPES, default='smp')
    address = models.TextField(help_text="Full smp://... or xftp://... URL")
    is_active = models.BooleanField(default=True)
    last_check = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.server_type.upper()})"
    
    def _parse_address(self):
        """Parse smp://fingerprint:password@host format"""
        # Pattern: smp://FINGERPRINT:PASSWORD@HOST or smp://FINGERPRINT@HOST
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
    def onion_address(self):
        return self.host
