"""
SimpleX CLI Client Models

Persistente Datenmodelle für Docker-basierte SimpleX CLI Clients
mit Verbindungs- und Nachrichtenverfolgung.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class SimplexClient(models.Model):
    """
    Ein SimpleX CLI Client in einem Docker Container.
    
    Jeder Client hat:
    - Einen eigenen Docker Container
    - Einen eigenen WebSocket Port (3031-3080)
    - Persistente Daten in einem Docker Volume
    - Konfigurierbare SMP Server
    """
    
    class Status(models.TextChoices):
        CREATED = 'created', 'Erstellt'
        STARTING = 'starting', 'Startet...'
        RUNNING = 'running', 'Läuft'
        STOPPING = 'stopping', 'Stoppt...'
        STOPPED = 'stopped', 'Gestoppt'
        ERROR = 'error', 'Fehler'
    
    # === Identifikation ===
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        verbose_name='Name',
        help_text='Anzeigename für diesen Client'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug',
        help_text='Eindeutiger Bezeichner (wird für Container-Namen verwendet)'
    )
    profile_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Profilname',
        help_text='SimpleX Chat Profilname (zufällig generiert)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Beschreibung',
        help_text='Optionale Beschreibung für diesen Client'
    )
    
    # === Docker Konfiguration ===
    container_id = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='Container ID',
        help_text='Docker Container ID (wird automatisch gesetzt)'
    )
    container_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Container Name',
        help_text='Docker Container Name (wird automatisch generiert)'
    )
    websocket_port = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(3031), MaxValueValidator(3080)],
        verbose_name='WebSocket Port',
        help_text='Port für WebSocket Verbindung (3031-3080)'
    )
    data_volume = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Data Volume',
        help_text='Docker Volume für persistente Daten'
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
        verbose_name='Letzter Fehler',
        help_text='Fehlermeldung falls Status = error'
    )
    
    # === Konfiguration ===
    smp_servers = models.ManyToManyField(
        'servers.Server',
        blank=True,
        related_name='cli_clients',
        verbose_name='SMP Server',
        help_text='SMP Server die dieser Client verwendet'
    )
    use_tor = models.BooleanField(
        default=True,
        verbose_name='Tor verwenden',
        help_text='Verbindung über Tor (SOCKS5 Proxy)'
    )
    
    # === Statistiken ===
    messages_sent = models.IntegerField(default=0, verbose_name='Gesendet')
    messages_received = models.IntegerField(default=0, verbose_name='Empfangen')
    messages_failed = models.IntegerField(default=0, verbose_name='Fehlgeschlagen')
    
    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Aktualisiert')
    last_active_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Zuletzt aktiv'
    )
    
    class Meta:
        verbose_name = 'SimpleX Client'
        verbose_name_plural = 'SimpleX Clients'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.slug})"
    
    # Profilnamen Pool
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
        
        # Auto-generiere Name und Slug wenn neu
        if self._state.adding:
            if not self.slug or not self.name:
                # Finde nächste freie Nummer
                existing_slugs = set(SimplexClient.objects.values_list('slug', flat=True))
                for i in range(1, 1000):
                    test_slug = f"client-{i:03d}"
                    if test_slug not in existing_slugs:
                        if not self.slug:
                            self.slug = test_slug
                        if not self.name:
                            self.name = f"Client {i:03d}"
                        break
        
        # Auto-generiere Profilname wenn leer
        if not self.profile_name:
            used_profiles = set(SimplexClient.objects.values_list('profile_name', flat=True))
            available = [p for p in self.PROFILE_NAMES if p not in used_profiles]
            if available:
                self.profile_name = random.choice(available)
            else:
                # Fallback: Zufällig mit Nummer
                self.profile_name = f"{random.choice(self.PROFILE_NAMES)}_{random.randint(100,999)}"
        
        # Auto-generiere container_name und data_volume
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
    def delivery_success_rate(self):
        """Berechnet Erfolgsrate der Nachrichtenzustellung"""
        total = self.messages_sent
        if total == 0:
            return 0.0
        return ((total - self.messages_failed) / total) * 100
    
    def update_stats(self, sent=0, received=0, failed=0):
        """Aktualisiert Statistiken"""
        self.messages_sent += sent
        self.messages_received += received
        self.messages_failed += failed
        self.last_active_at = timezone.now()
        self.save(update_fields=['messages_sent', 'messages_received', 
                                  'messages_failed', 'last_active_at', 'updated_at'])


class ClientConnection(models.Model):
    """
    Verbindung zwischen zwei SimpleX Clients.
    
    SimpleX Verbindungen sind bidirektional - wenn A zu B verbindet,
    kann B auch an A senden. Wir tracken beide Seiten.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ausstehend'
        CONNECTING = 'connecting', 'Verbindet...'
        CONNECTED = 'connected', 'Verbunden'
        FAILED = 'failed', 'Fehlgeschlagen'
        DELETED = 'deleted', 'Gelöscht'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Die beiden Clients
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
        verbose_name='Client B (Akzeptierer)'
    )
    
    # Einladungslink (von Client A erstellt)
    invitation_link = models.TextField(
        blank=True,
        verbose_name='Einladungslink'
    )
    
    # Kontaktnamen (wie sie sich gegenseitig sehen)
    contact_name_on_a = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Name auf A',
        help_text='Wie Client A den Client B sieht'
    )
    contact_name_on_b = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Name auf B',
        help_text='Wie Client B den Client A sieht'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Status'
    )
    last_error = models.TextField(blank=True, verbose_name='Letzter Fehler')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    connected_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Client Verbindung'
        verbose_name_plural = 'Client Verbindungen'
        unique_together = ['client_a', 'client_b']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client_a.name} ↔ {self.client_b.name}"
    
    @property
    def is_connected(self):
        return self.status == self.Status.CONNECTED


class TestMessage(models.Model):
    """
    Eine Test-Nachricht zwischen zwei verbundenen Clients.
    
    Trackt den vollständigen Delivery-Lifecycle:
    - ⏳ sending: Wird gesendet
    - ✓ sent: Server hat empfangen
    - ✓✓ delivered: Client hat empfangen
    - ❌ failed: Zustellung fehlgeschlagen
    """
    
    class DeliveryStatus(models.TextChoices):
        SENDING = 'sending', '⏳ Wird gesendet'
        SENT = 'sent', '✓ Server empfangen'
        DELIVERED = 'delivered', '✓✓ Client empfangen'
        FAILED = 'failed', '❌ Fehlgeschlagen'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Verbindung über die gesendet wird
    connection = models.ForeignKey(
        ClientConnection,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Verbindung'
    )
    
    # Sender und Empfänger
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
        verbose_name='Empfänger'
    )
    
    # Nachrichteninhalt
    content = models.TextField(verbose_name='Inhalt')
    
    # Correlation ID für WebSocket Tracking
    correlation_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Correlation ID'
    )
    
    # Delivery Status
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.SENDING,
        verbose_name='Zustellstatus'
    )
    
    # Timestamps für Latenz-Berechnung
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Gesendet um'
    )
    server_received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Server empfangen um'
    )
    client_received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Client empfangen um'
    )
    
    # Berechnete Latenzen (in Millisekunden)
    latency_to_server_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Latenz zum Server (ms)'
    )
    latency_to_client_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Latenz zum Client (ms)'
    )
    total_latency_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Gesamtlatenz (ms)'
    )
    
    # Fehlerinfo
    error_message = models.TextField(blank=True, verbose_name='Fehlermeldung')
    
    # Optional: Referenz zu einem Stress-Test Run
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
        verbose_name = 'Test Nachricht'
        verbose_name_plural = 'Test Nachrichten'
        ordering = ['-created_at']
    
    def __str__(self):
        status_icon = {
            'sending': '⏳',
            'sent': '✓',
            'delivered': '✓✓',
            'failed': '❌'
        }.get(self.delivery_status, '?')
        return f"{status_icon} {self.sender.name} → {self.recipient.name}"
    
    def mark_sent(self):
        """Markiert Nachricht als vom Server empfangen (✓)"""
        now = timezone.now()
        self.delivery_status = self.DeliveryStatus.SENT
        self.server_received_at = now
        if self.sent_at:
            self.latency_to_server_ms = int((now - self.sent_at).total_seconds() * 1000)
        self.save()
    
    def mark_delivered(self):
        """Markiert Nachricht als vom Client empfangen (✓✓)"""
        now = timezone.now()
        self.delivery_status = self.DeliveryStatus.DELIVERED
        self.client_received_at = now
        if self.server_received_at:
            self.latency_to_client_ms = int((now - self.server_received_at).total_seconds() * 1000)
        if self.sent_at:
            self.total_latency_ms = int((now - self.sent_at).total_seconds() * 1000)
        self.save()
        
        # Update sender stats
        self.sender.update_stats(sent=0, received=0, failed=0)  # Just touch last_active
        self.recipient.update_stats(received=1)
    
    def mark_failed(self, error: str = ''):
        """Markiert Nachricht als fehlgeschlagen (❌)"""
        self.delivery_status = self.DeliveryStatus.FAILED
        self.error_message = error
        self.save()
        self.sender.update_stats(failed=1)


class DeliveryReceipt(models.Model):
    """
    Explizites Tracking von Delivery Receipts.
    
    SimpleX sendet asynchrone Events wenn:
    - Server die Nachricht empfangen hat
    - Client die Nachricht empfangen hat
    
    Diese werden hier separat geloggt für detailliertes Debugging.
    """
    
    class ReceiptType(models.TextChoices):
        SERVER_ACK = 'server_ack', 'Server Acknowledgment'
        CLIENT_ACK = 'client_ack', 'Client Acknowledgment'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    message = models.ForeignKey(
        TestMessage,
        on_delete=models.CASCADE,
        related_name='receipts',
        verbose_name='Nachricht'
    )
    
    receipt_type = models.CharField(
        max_length=20,
        choices=ReceiptType.choices,
        verbose_name='Receipt Typ'
    )
    
    # Raw Event Data (für Debugging)
    raw_event = models.JSONField(
        default=dict,
        verbose_name='Raw Event',
        help_text='Original SimpleX Event JSON'
    )
    
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Delivery Receipt'
        verbose_name_plural = 'Delivery Receipts'
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.get_receipt_type_display()} für {self.message}"
