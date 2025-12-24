from django.db import models
from servers.models import Server

class TestRun(models.Model):
    """Ein Stresstest-Durchlauf"""
    STATUS_CHOICES = [
        ('pending', 'Ausstehend'),
        ('running', 'Läuft'),
        ('completed', 'Abgeschlossen'),
        ('failed', 'Fehlgeschlagen'),
        ('cancelled', 'Abgebrochen'),
    ]
    
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Konfiguration
    num_clients = models.PositiveIntegerField(default=2)
    duration_seconds = models.PositiveIntegerField(default=60)
    message_interval_seconds = models.PositiveIntegerField(default=5)
    
    # Ergebnisse
    messages_sent = models.PositiveIntegerField(default=0)
    messages_received = models.PositiveIntegerField(default=0)
    avg_latency_ms = models.FloatField(null=True, blank=True)
    min_latency_ms = models.FloatField(null=True, blank=True)
    max_latency_ms = models.FloatField(null=True, blank=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    servers = models.ManyToManyField(Server, related_name='test_runs', blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    @property
    def delivery_rate(self):
        if self.messages_sent == 0:
            return 0
        return round((self.messages_received / self.messages_sent) * 100, 1)


class Metric(models.Model):
    """Echtzeit-Metriken während eines Tests"""
    test_run = models.ForeignKey(TestRun, on_delete=models.CASCADE, related_name='metrics')
    timestamp = models.DateTimeField(auto_now_add=True)
    metric_type = models.CharField(max_length=50)  # latency, sent, received, error
    value = models.FloatField()
    client_id = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
