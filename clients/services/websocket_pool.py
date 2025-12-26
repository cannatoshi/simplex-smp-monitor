"""
WebSocket Pool für SimpleX CLI Clients

Verwaltet WebSocket-Verbindungen zu allen laufenden CLI Containern:
- Connection Pool mit automatischem Reconnect
- Command/Response Handling mit Correlation IDs
- Async Event Listener für Delivery Receipts
- Thread-safe Message Sending

SimpleX Chat WebSocket Protocol:
- Request:  {"corrId": "unique_id", "cmd": "command_string"}
- Response: {"corrId": "unique_id", "resp": {...}}
- Event:    {"corrId": null, "resp": {...}}  (async events)
"""

import asyncio
import json
import logging
import uuid
import websockets
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class PendingCommand:
    """Tracking für ausstehende Commands"""
    correlation_id: str
    command: str
    sent_at: datetime
    future: asyncio.Future
    timeout: float = 30.0


@dataclass 
class ClientConnection:
    """WebSocket Verbindung zu einem Client"""
    client_id: str
    client_slug: str
    websocket_url: str
    websocket: Optional[websockets.WebSocketClientProtocol] = None
    connected: bool = False
    pending_commands: Dict[str, PendingCommand] = field(default_factory=dict)
    event_handlers: List[Callable] = field(default_factory=list)
    reconnect_attempts: int = 0
    max_reconnect_attempts: int = 5


class WebSocketPool:
    """
    Pool für WebSocket-Verbindungen zu SimpleX CLI Clients.
    
    Features:
    - Automatisches Connection Management
    - Correlation ID basiertes Request/Response
    - Async Event Handling für Delivery Receipts
    - Thread-safe für Django Views
    """
    
    def __init__(self):
        self.connections: Dict[str, ClientConnection] = {}
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._running = False
        self._global_event_handlers: List[Callable] = []
        
    async def connect(self, simplex_client) -> bool:
        """
        Verbindet zu einem SimpleX Client.
        
        Args:
            simplex_client: SimplexClient Model-Instanz
            
        Returns:
            True wenn erfolgreich verbunden
        """
        client_id = str(simplex_client.id)
        
        if client_id in self.connections and self.connections[client_id].connected:
            logger.debug(f"Bereits verbunden: {simplex_client.slug}")
            return True
        
        conn = ClientConnection(
            client_id=client_id,
            client_slug=simplex_client.slug,
            websocket_url=simplex_client.websocket_url
        )
        
        try:
            conn.websocket = await websockets.connect(
                conn.websocket_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5
            )
            conn.connected = True
            conn.reconnect_attempts = 0
            self.connections[client_id] = conn
            
            # Starte Listener Task
            asyncio.create_task(self._listen(client_id))
            
            logger.info(f"WebSocket verbunden: {simplex_client.slug} ({conn.websocket_url})")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket Verbindung fehlgeschlagen: {simplex_client.slug} - {e}")
            conn.connected = False
            conn.reconnect_attempts += 1
            return False
    
    async def disconnect(self, simplex_client) -> None:
        """Trennt die Verbindung zu einem Client"""
        client_id = str(simplex_client.id)
        
        if client_id in self.connections:
            conn = self.connections[client_id]
            if conn.websocket:
                await conn.websocket.close()
            conn.connected = False
            del self.connections[client_id]
            logger.info(f"WebSocket getrennt: {simplex_client.slug}")
    
    async def send_command(self, simplex_client, command: str, 
                          timeout: float = 30.0) -> Dict[str, Any]:
        """
        Sendet einen Command und wartet auf Response.
        
        Args:
            simplex_client: SimplexClient Model-Instanz
            command: SimpleX CLI Command (z.B. "/c", "@user message")
            timeout: Timeout in Sekunden
            
        Returns:
            Response Dict von SimpleX
        """
        client_id = str(simplex_client.id)
        
        if client_id not in self.connections or not self.connections[client_id].connected:
            if not await self.connect(simplex_client):
                raise ConnectionError(f"Nicht verbunden: {simplex_client.slug}")
        
        conn = self.connections[client_id]
        
        # Correlation ID generieren
        corr_id = f"cmd_{uuid.uuid4().hex[:12]}"
        
        # Request erstellen
        request = {
            "corrId": corr_id,
            "cmd": command
        }
        
        # Future für Response
        future = asyncio.get_event_loop().create_future()
        
        pending = PendingCommand(
            correlation_id=corr_id,
            command=command,
            sent_at=datetime.now(),
            future=future,
            timeout=timeout
        )
        conn.pending_commands[corr_id] = pending
        
        try:
            # Request senden
            await conn.websocket.send(json.dumps(request))
            logger.debug(f"Command gesendet: {command[:50]}... ({corr_id})")
            
            # Auf Response warten
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Command Timeout: {command[:50]}... ({corr_id})")
            raise TimeoutError(f"Keine Antwort innerhalb von {timeout}s")
            
        finally:
            conn.pending_commands.pop(corr_id, None)
    
    async def send_message(self, sender, recipient_name: str, 
                          content: str) -> str:
        """
        Sendet eine Nachricht von einem Client an einen Kontakt.
        
        Args:
            sender: SimplexClient Model-Instanz (Sender)
            recipient_name: Kontaktname beim Sender
            content: Nachrichteninhalt
            
        Returns:
            Correlation ID für Tracking
        """
        command = f"@{recipient_name} {content}"
        response = await self.send_command(sender, command)
        
        # Correlation ID aus Response extrahieren
        corr_id = response.get('corrId', '')
        
        return corr_id
    
    async def create_invitation(self, simplex_client) -> str:
        """
        Erstellt einen Einladungslink.
        
        Args:
            simplex_client: SimplexClient Model-Instanz
            
        Returns:
            Einladungslink
        """
        response = await self.send_command(simplex_client, "/c")
        
        # Link aus Response extrahieren
        # Response format: {"resp": {"type": "invitation", "link": "simplex:/..."}}
        resp_data = response.get('resp', {})
        
        if isinstance(resp_data, dict) and 'connReqInvitation' in str(resp_data):
            # Parse invitation link from response
            # The actual format depends on SimpleX version
            link = resp_data.get('connReqInvitation', '')
            return link
        
        raise ValueError(f"Unerwartete Response: {response}")
    
    async def accept_invitation(self, simplex_client, invitation_link: str) -> str:
        """
        Akzeptiert eine Einladung.
        
        Args:
            simplex_client: SimplexClient Model-Instanz
            invitation_link: SimpleX Einladungslink
            
        Returns:
            Kontaktname
        """
        command = f"/c {invitation_link}"
        response = await self.send_command(simplex_client, command)
        
        # Kontaktname aus Response extrahieren
        resp_data = response.get('resp', {})
        contact_name = resp_data.get('contact', {}).get('localDisplayName', '')
        
        return contact_name
    
    async def _listen(self, client_id: str) -> None:
        """
        Listener Task für eingehende Messages/Events.
        
        Verarbeitet:
        - Responses auf ausstehende Commands
        - Async Events (Delivery Receipts etc.)
        """
        if client_id not in self.connections:
            return
        
        conn = self.connections[client_id]
        
        try:
            async for message in conn.websocket:
                try:
                    data = json.loads(message)
                    corr_id = data.get('corrId')
                    
                    if corr_id and corr_id in conn.pending_commands:
                        # Response auf ausstehenden Command
                        pending = conn.pending_commands[corr_id]
                        if not pending.future.done():
                            pending.future.set_result(data)
                    else:
                        # Async Event
                        await self._handle_event(client_id, data)
                        
                except json.JSONDecodeError:
                    logger.warning(f"Ungültige JSON Message: {message[:100]}")
                    
        except websockets.ConnectionClosed:
            logger.info(f"WebSocket Verbindung geschlossen: {conn.client_slug}")
            conn.connected = False
            
            # Auto-Reconnect versuchen
            if conn.reconnect_attempts < conn.max_reconnect_attempts:
                await asyncio.sleep(2 ** conn.reconnect_attempts)
                # Reconnect wird beim nächsten Command versucht
                
        except Exception as e:
            logger.error(f"WebSocket Listener Fehler: {e}")
            conn.connected = False
    
    async def _handle_event(self, client_id: str, event: Dict[str, Any]) -> None:
        """
        Verarbeitet async Events von SimpleX.
        
        Wichtige Events:
        - MsgDeliveryEvent: Nachricht an Server zugestellt
        - RcvMsgEvent: Nachricht empfangen
        """
        resp = event.get('resp', {})
        event_type = resp.get('type', '')
        
        logger.debug(f"Event empfangen [{client_id}]: {event_type}")
        
        # Global Event Handlers aufrufen
        for handler in self._global_event_handlers:
            try:
                await handler(client_id, event)
            except Exception as e:
                logger.error(f"Event Handler Fehler: {e}")
        
        # Connection-spezifische Handler
        if client_id in self.connections:
            for handler in self.connections[client_id].event_handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event Handler Fehler: {e}")
    
    def add_event_handler(self, handler: Callable) -> None:
        """Registriert einen globalen Event Handler"""
        self._global_event_handlers.append(handler)
    
    def remove_event_handler(self, handler: Callable) -> None:
        """Entfernt einen globalen Event Handler"""
        if handler in self._global_event_handlers:
            self._global_event_handlers.remove(handler)
    
    # === Synchrone Wrapper für Django Views ===
    
    def send_command_sync(self, simplex_client, command: str, 
                         timeout: float = 30.0) -> Dict[str, Any]:
        """Synchroner Wrapper für send_command"""
        loop = self._get_or_create_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.send_command(simplex_client, command, timeout),
            loop
        )
        return future.result(timeout=timeout + 5)
    
    def send_message_sync(self, sender, recipient_name: str, 
                         content: str) -> str:
        """Synchroner Wrapper für send_message"""
        loop = self._get_or_create_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.send_message(sender, recipient_name, content),
            loop
        )
        return future.result(timeout=35)
    
    def connect_sync(self, simplex_client) -> bool:
        """Synchroner Wrapper für connect"""
        loop = self._get_or_create_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.connect(simplex_client),
            loop
        )
        return future.result(timeout=10)
    
    def _get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """Holt oder erstellt den Event Loop"""
        if self.event_loop is None or self.event_loop.is_closed():
            self.event_loop = asyncio.new_event_loop()
            # Loop in separatem Thread starten
            import threading
            thread = threading.Thread(target=self.event_loop.run_forever, daemon=True)
            thread.start()
        return self.event_loop
    
    def get_status(self) -> Dict[str, Any]:
        """Gibt Status-Übersicht aller Verbindungen zurück"""
        return {
            'total_connections': len(self.connections),
            'connected': sum(1 for c in self.connections.values() if c.connected),
            'connections': {
                slug: {
                    'connected': conn.connected,
                    'pending_commands': len(conn.pending_commands),
                    'reconnect_attempts': conn.reconnect_attempts,
                }
                for slug, conn in self.connections.items()
            }
        }
    
    async def disconnect_all(self) -> None:
        """Trennt alle Verbindungen"""
        for client_id in list(self.connections.keys()):
            if self.connections[client_id].websocket:
                await self.connections[client_id].websocket.close()
        self.connections.clear()
        logger.info("Alle WebSocket Verbindungen getrennt")


# Singleton-Instanz
_websocket_pool: Optional[WebSocketPool] = None


def get_websocket_pool() -> WebSocketPool:
    """Gibt die WebSocket Pool Singleton-Instanz zurück"""
    global _websocket_pool
    if _websocket_pool is None:
        _websocket_pool = WebSocketPool()
    return _websocket_pool


# === Event Handler für Delivery Receipts ===

async def delivery_receipt_handler(client_id: str, event: Dict[str, Any]) -> None:
    """
    Verarbeitet Delivery Receipt Events.
    
    Aktualisiert TestMessage Status:
    - sndMsgDelivered → mark_sent() (✓ Server)
    - newRcvMsg → mark_delivered() (✓✓ Client)
    """
    from clients.models import TestMessage, DeliveryReceipt
    
    resp = event.get('resp', {})
    event_type = resp.get('type', '')
    
    if event_type == 'sndMsgDelivered':
        # Nachricht wurde an Server zugestellt
        # TODO: Find message by correlation and mark_sent()
        logger.debug(f"Server Delivery Receipt: {resp}")
        
    elif event_type == 'newRcvMsg':
        # Nachricht wurde empfangen
        # TODO: Process received message
        logger.debug(f"Message Received: {resp}")


# Registriere Handler beim Import
def _register_default_handlers():
    pool = get_websocket_pool()
    pool.add_event_handler(delivery_receipt_handler)

# Lazy registration - wird bei erstem Zugriff aufgerufen
