from django.db import models

class EventLog(models.Model):
    """Ereignis-Protokollierung"""
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO', db_index=True)
    source = models.CharField(max_length=100, db_index=True)
    message = models.TextField()
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.level}] {self.source}: {self.message[:50]}"
    
    @classmethod
    def log(cls, level, source, message, details=None):
        return cls.objects.create(level=level, source=source, message=message, details=details)
    
    @classmethod
    def info(cls, source, message, details=None):
        return cls.log('INFO', source, message, details)
    
    @classmethod
    def error(cls, source, message, details=None):
        return cls.log('ERROR', source, message, details)
    
    @classmethod
    def warning(cls, source, message, details=None):
        return cls.log('WARNING', source, message, details)
