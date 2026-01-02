"""
SimpleX CLI Client Models

Persistent data models for Docker-based SimpleX CLI clients
with connection and message tracking.
"""

from django.db import models
from django.db.models import Avg, Min, Max
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class SimplexClient(models.Model):
    """
    A SimpleX CLI client running in a Docker container.
    
    Each client has:
    - Its own Docker container
    - Its own WebSocket port (3031-3080)
    - Persistent data in a Docker volume
    - Configurable SMP servers
    """
    
    class Status(models.TextChoices):
        CREATED = 'created', 'Created'
        STARTING = 'starting', 'Starting...'
        RUNNING = 'running', 'Running'
        STOPPING = 'stopping', 'Stopping...'
        STOPPED = 'stopped', 'Stopped'
        ERROR = 'error', 'Error'
    
    # === Identification ===
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        verbose_name='Name',
        help_text='Display name for this client'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug',
        help_text='Unique identifier (used for container names)'
    )
    profile_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Profile Name',
        help_text='SimpleX Chat profile name (randomly generated)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Optional description for this client'
    )
    
    # === Docker Configuration ===
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
    websocket_port = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(3031), MaxValueValidator(3080)],
        verbose_name='WebSocket Port',
        help_text='Port for WebSocket connection (3031-3080)'
    )
    data_volume = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Data Volume',
        help_text='Docker volume for persistent data'
    )
    
    # === Status ===
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        verbose_name='Status'
    )
    last_error = models.TextField(
        blank=True,
        verbose_name='Last Error',
        help_text='Error message if status = error'
    )
    
    # === Configuration ===
    smp_servers = models.ManyToManyField(
        'servers.Server',
        blank=True,
        related_name='cli_clients',
        verbose_name='SMP Servers',
        help_text='SMP servers this client uses'
    )
    use_tor = models.BooleanField(
        default=True,
        verbose_name='Use Tor',
        help_text='Connect via Tor (SOCKS5 proxy)'
    )
    
    # === Statistics ===
    messages_sent = models.IntegerField(default=0, verbose_name='Sent')
    messages_received = models.IntegerField(default=0, verbose_name='Received')
    messages_failed = models.IntegerField(default=0, verbose_name='Failed')
    
    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated')
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Started At',
        help_text='Last start time (for uptime calculation)'
    )
    last_active_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Last Active'
    )
    
    class Meta:
        verbose_name = 'SimpleX Client'
        verbose_name_plural = 'SimpleX Clients'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.slug})"
    
    # Profile name pool
    PROFILE_NAMES = [
        'alice', 'bob', 'chris', 'diana', 'eve', 'frank', 'grace', 'henry',
        'iris', 'jack', 'kate', 'leo', 'maria', 'nick', 'olivia', 'peter',
        'quinn', 'rosa', 'sam', 'tara', 'uma', 'victor', 'wendy', 'xander',
        'yara', 'zack', 'amber', 'ben', 'clara', 'david', 'emma', 'felix',
        'gina', 'hugo', 'ida', 'james', 'kim', 'luke', 'mia', 'noah',
        'ora', 'paul', 'qiana', 'rick', 'sara', 'tom', 'uri', 'vera'
    ]
    
    def save(self, *args, **kwargs):
        import random
        
        # Auto-generate name and slug if new
        if self._state.adding:
            if not self.slug or not self.name:
                # Find next free number
                existing_slugs = set(SimplexClient.objects.values_list('slug', flat=True))
                for i in range(1, 1000):
                    test_slug = f"client-{i:03d}"
                    if test_slug not in existing_slugs:
                        if not self.slug:
                            self.slug = test_slug
                        if not self.name:
                            self.name = f"Client {i:03d}"
                        break
        
        # Auto-generate profile name if empty
        if not self.profile_name:
            used_profiles = set(SimplexClient.objects.values_list('profile_name', flat=True))
            available = [p for p in self.PROFILE_NAMES if p not in used_profiles]
            if available:
                self.profile_name = random.choice(available)
            else:
                # Fallback: random with number
                self.profile_name = f"{random.choice(self.PROFILE_NAMES)}_{random.randint(100,999)}"
        
        # Auto-generate container_name and data_volume
        if not self.container_name:
            self.container_name = f"simplex-client-{self.slug}"
        if not self.data_volume:
            self.data_volume = f"simplex-client-{self.slug}-data"
        
        super().save(*args, **kwargs)
    
    @property
    def is_running(self):
        return self.status == self.Status.RUNNING
    
    @property
    def websocket_url(self):
        return f"ws://localhost:{self.websocket_port}"
    
    @property
    def data_volume_name(self):
        """Alias for data_volume (template compatibility)"""
        return self.data_volume
    
    @property
    def last_activity(self):
        """Alias for last_active_at (template compatibility)"""
        return self.last_active_at
    
    @property
    def delivery_success_rate(self):
        """Calculate message delivery success rate"""
        total = self.messages_sent
        if total == 0:
            return 0.0
        return ((total - self.messages_failed) / total) * 100

    @property
    def uptime_display(self):
        """Formatted uptime as readable string"""
        if not self.started_at or self.status != 'running':
            return None
        
        delta = timezone.now() - self.started_at
        secs = int(delta.total_seconds())
        
        if secs < 60:
            return f"{secs}s"
        elif secs < 3600:
            return f"{secs // 60}m"
        elif secs < 86400:
            hours = secs // 3600
            mins = (secs % 3600) // 60
            return f"{hours}h {mins}m"
        else:
            days = secs // 86400
            hours = (secs % 86400) // 3600
            return f"{days}d {hours}h"
    
    @property
    def avg_latency_ms(self):
        """Average latency in milliseconds"""
        result = self.sent_messages.filter(
            total_latency_ms__isnull=False
        ).aggregate(avg=Avg('total_latency_ms'))
        return result['avg']
    
    @property
    def min_latency_ms(self):
        """Minimum latency in milliseconds"""
        result = self.sent_messages.filter(
            total_latency_ms__isnull=False
        ).aggregate(min=Min('total_latency_ms'))
        return result['min']
    
    @property
    def max_latency_ms(self):
        """Maximum latency in milliseconds"""
        result = self.sent_messages.filter(
            total_latency_ms__isnull=False
        ).aggregate(max=Max('total_latency_ms'))
        return result['max']
    
    @property
    def messages_delivered(self):
        """Number of successfully delivered messages"""
        return self.messages_sent - self.messages_failed
    
    @property
    def last_message_received(self):
        """Timestamp of last received message"""
        last_msg = self.received_messages.order_by('-client_received_at').first()
        if last_msg and last_msg.client_received_at:
            return last_msg.client_received_at
        return None
    
    def start(self):
        """Set status to running and save start time"""
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.last_error = ''
        self.save(update_fields=['status', 'started_at', 'last_error', 'updated_at'])
    
    def stop(self):
        """Set status to stopped"""
        self.status = self.Status.STOPPED
        self.save(update_fields=['status', 'updated_at'])
    
    def set_error(self, error_message: str):
        """Set status to error with error message"""
        self.status = self.Status.ERROR
        self.last_error = error_message
        self.save(update_fields=['status', 'last_error', 'updated_at'])
    
    def update_stats(self, sent=0, received=0, failed=0):
        """Update statistics"""
        self.messages_sent += sent
        self.messages_received += received
        self.messages_failed += failed
        self.last_active_at = timezone.now()
        self.save(update_fields=['messages_sent', 'messages_received', 
                                  'messages_failed', 'last_active_at', 'updated_at'])


class ClientConnection(models.Model):
    """
    Connection between two SimpleX clients.
    
    SimpleX connections are bidirectional - when A connects to B,
    B can also send to A. We track both sides.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONNECTING = 'connecting', 'Connecting...'
        CONNECTED = 'connected', 'Connected'
        FAILED = 'failed', 'Failed'
        DELETED = 'deleted', 'Deleted'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # The two clients
    client_a = models.ForeignKey(
        SimplexClient,
        on_delete=models.CASCADE,
        related_name='connections_as_a',
        verbose_name='Client A (Initiator)'
    )
    client_b = models.ForeignKey(
        SimplexClient,
        on_delete=models.CASCADE,
        related_name='connections_as_b',
        verbose_name='Client B (Acceptor)'
    )
    
    # Invitation link (created by Client A)
    invitation_link = models.TextField(
        blank=True,
        verbose_name='Invitation Link'
    )
    
    # Contact names (how they see each other)
    contact_name_on_a = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Name on A',
        help_text='How Client A sees Client B'
    )
    contact_name_on_b = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Name on B',
        help_text='How Client B sees Client A'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Status'
    )
    last_error = models.TextField(blank=True, verbose_name='Last Error')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    connected_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Client Connection'
        verbose_name_plural = 'Client Connections'
        unique_together = ['client_a', 'client_b']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client_a.name} ↔ {self.client_b.name}"
    
    @property
    def is_connected(self):
        return self.status == self.Status.CONNECTED


class TestMessage(models.Model):
    """
    A test message between two connected clients.
    
    Tracks the complete delivery lifecycle:
    - ⏳ sending: Being sent
    - ✓ sent: Server received
    - ✓✓ delivered: Client received
    - ❌ failed: Delivery failed
    """
    
    class DeliveryStatus(models.TextChoices):
        SENDING = 'sending', '⏳ Sending'
        SENT = 'sent', '✓ Server received'
        DELIVERED = 'delivered', '✓✓ Client received'
        FAILED = 'failed', '❌ Failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Connection used for sending
    connection = models.ForeignKey(
        ClientConnection,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Connection'
    )
    
    # Sender and recipient
    sender = models.ForeignKey(
        SimplexClient,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Sender'
    )
    recipient = models.ForeignKey(
        SimplexClient,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Recipient'
    )
    
    # Message content
    content = models.TextField(verbose_name='Content')
    
    # Legacy correlation ID for WebSocket tracking
    correlation_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Correlation ID'
    )
    
    # NEW: Unique tracking ID for reliable message matching
    tracking_id = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        verbose_name='Tracking ID',
        help_text='Unique ID for message tracking (msg_xxxxxxxxxxxx)'
    )
    
    # Delivery status
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.SENDING,
        verbose_name='Delivery Status'
    )
    
    # Timestamps for latency calculation
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Sent At'
    )
    server_received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Server Received At'
    )
    client_received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Client Received At'
    )
    
    # Calculated latencies (in milliseconds)
    latency_to_server_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Latency to Server (ms)'
    )
    latency_to_client_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Latency to Client (ms)'
    )
    total_latency_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Total Latency (ms)'
    )
    
    # Error info
    error_message = models.TextField(blank=True, verbose_name='Error Message')
    
    # Optional: Reference to a stress test run
    test_run = models.ForeignKey(
        'stresstests.TestRun',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cli_messages',
        verbose_name='Test Run'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Test Message'
        verbose_name_plural = 'Test Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        status_icon = {
            'sending': '⏳',
            'sent': '✓',
            'delivered': '✓✓',
            'failed': '❌'
        }.get(self.delivery_status, '?')
        return f"{status_icon} {self.sender.name} → {self.recipient.name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate tracking_id if not set
        if not self.tracking_id:
            self.tracking_id = f"msg_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)
    
    @property
    def recipient_name(self):
        """Recipient name (for template)"""
        return self.recipient.name if self.recipient else 'Unknown'
    
    @property
    def sender_name(self):
        """Sender name (for template)"""
        return self.sender.name if self.sender else 'Unknown'
    
    @property
    def contact_name(self):
        """Contact name (for 'All' tab)"""
        return self.recipient.name if hasattr(self, '_direction') and self._direction == 'sent' else self.sender.name
    
    @property
    def direction(self):
        """Message direction (for template)"""
        return getattr(self, '_direction', 'sent')
    
    @property
    def received_at(self):
        """Alias for client_received_at (template compatibility)"""
        return self.client_received_at or self.created_at
    
    @property
    def content_without_tracking(self):
        """Message content without the tracking ID prefix"""
        import re
        return re.sub(r'^\[msg_[a-f0-9]+\]\s*', '', self.content)
    
    def mark_sent(self):
        """Mark message as received by server (✓)"""
        now = timezone.now()
        self.delivery_status = self.DeliveryStatus.SENT
        self.server_received_at = now
        if self.sent_at:
            self.latency_to_server_ms = int((now - self.sent_at).total_seconds() * 1000)
        self.save()
    
    def mark_delivered(self):
        """Mark message as received by client (✓✓)"""
        now = timezone.now()
        self.delivery_status = self.DeliveryStatus.DELIVERED
        self.client_received_at = now
        if self.server_received_at:
            self.latency_to_client_ms = int((now - self.server_received_at).total_seconds() * 1000)
        if self.sent_at:
            self.total_latency_ms = int((now - self.sent_at).total_seconds() * 1000)
        self.save()
    
    def mark_failed(self, error: str = ''):
        """Mark message as failed (❌)"""
        self.delivery_status = self.DeliveryStatus.FAILED
        self.error_message = error
        self.save()
        self.sender.update_stats(failed=1)


class DeliveryReceipt(models.Model):
    """
    Explicit tracking of delivery receipts.
    
    SimpleX sends async events when:
    - Server has received the message
    - Client has received the message
    
    These are logged separately here for detailed debugging.
    """
    
    class ReceiptType(models.TextChoices):
        SERVER_ACK = 'server_ack', 'Server Acknowledgment'
        CLIENT_ACK = 'client_ack', 'Client Acknowledgment'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    message = models.ForeignKey(
        TestMessage,
        on_delete=models.CASCADE,
        related_name='receipts',
        verbose_name='Message'
    )
    
    receipt_type = models.CharField(
        max_length=20,
        choices=ReceiptType.choices,
        verbose_name='Receipt Type'
    )
    
    # Raw event data (for debugging)
    raw_event = models.JSONField(
        default=dict,
        verbose_name='Raw Event',
        help_text='Original SimpleX event JSON'
    )
    
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Delivery Receipt'
        verbose_name_plural = 'Delivery Receipts'
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.get_receipt_type_display()} for {self.message}"