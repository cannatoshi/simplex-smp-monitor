"""
SimpleX Chat Command Service

Synchroner Service für SimpleX CLI Commands via WebSocket.
Wird von Django Views aufgerufen.
"""

import json
import logging
import uuid
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Ergebnis eines SimpleX Commands"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    raw_response: Optional[Dict] = None


class SimplexCommandService:
    """
    Synchroner Service für SimpleX CLI WebSocket Commands.
    """
    
    def __init__(self):
        self._loop = None
    
    def _get_loop(self):
        """Holt oder erstellt Event Loop"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def _run_async(self, coro):
        """Führt async Coroutine synchron aus"""
        loop = self._get_loop()
        return loop.run_until_complete(coro)
    
    async def _send_command(self, ws_url: str, command: str, timeout: float = 30.0) -> CommandResult:
        """Sendet Command via WebSocket und wartet auf Antwort."""
        import websockets
        
        corr_id = str(uuid.uuid4())[:8]
        request = json.dumps({"corrId": corr_id, "cmd": command})
        
        try:
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                # Initiale Events überspringen
                try:
                    while True:
                        msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                        data = json.loads(msg)
                        if data.get("corrId") == corr_id:
                            break
                except asyncio.TimeoutError:
                    pass
                
                # Command senden
                await ws.send(request)
                logger.debug(f"Sent: {request}")
                
                # Auf Antwort warten
                start_time = asyncio.get_event_loop().time()
                while True:
                    remaining = timeout - (asyncio.get_event_loop().time() - start_time)
                    if remaining <= 0:
                        return CommandResult(success=False, data={}, error="Timeout")
                    
                    msg = await asyncio.wait_for(ws.recv(), timeout=remaining)
                    data = json.loads(msg)
                    logger.debug(f"Received: {data}")
                    
                    if data.get("corrId") == corr_id:
                        resp = data.get("resp", {})
                        resp_type = resp.get("type", "")
                        
                        if resp_type == "chatCmdError":
                            error_info = resp.get("chatError", {})
                            error_type = error_info.get("errorType", {})
                            error_msg = error_type.get("message", str(error_type))
                            return CommandResult(success=False, data={}, error=error_msg, raw_response=data)
                        
                        return CommandResult(success=True, data=resp, raw_response=data)
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            return CommandResult(success=False, data={}, error=str(e))
    
    # === Public API ===
    
    def create_address(self, client) -> CommandResult:
        """Erstellt einen Einladungslink für einen Client."""
        result = self._run_async(self._send_command(client.websocket_url, "/address"))
        
        if result.success:
            conn_link = result.data.get("connLinkContact", {})
            result.data = {
                "full_link": conn_link.get("connFullLink", ""),
                "short_link": conn_link.get("connShortLink", ""),
            }
        return result
    
    def get_address(self, client) -> CommandResult:
        """Holt die existierende Adresse eines Clients."""
        return self._run_async(self._send_command(client.websocket_url, "/show_address"))
    
    def connect_via_link(self, client, invitation_link: str) -> CommandResult:
        """Verbindet Client mit einem Einladungslink."""
        return self._run_async(self._send_command(client.websocket_url, f"/connect {invitation_link}"))
    
    def send_message(self, client, contact_name: str, message: str) -> CommandResult:
        """Sendet eine Nachricht an einen Kontakt."""
        return self._run_async(self._send_command(client.websocket_url, f"@{contact_name} {message}"))
    
    def get_contacts(self, client) -> CommandResult:
        """Listet alle Kontakte eines Clients."""
        return self._run_async(self._send_command(client.websocket_url, "/contacts"))
    
    def accept_contact(self, client, contact_name: str) -> CommandResult:
        """Akzeptiert eine ausstehende Kontaktanfrage."""
        return self._run_async(self._send_command(client.websocket_url, f"/accept {contact_name}"))
    
    def enable_auto_accept(self, client) -> CommandResult:
        """Aktiviert Auto-Accept für eingehende Kontaktanfragen."""
        return self._run_async(self._send_command(client.websocket_url, "/auto_accept on"))
    
    def create_or_get_address(self, client) -> CommandResult:
        """Erstellt eine Adresse oder holt die existierende."""
        result = self._run_async(self._send_command(client.websocket_url, "/address"))
        
        # Falls schon existiert, hole sie
        if not result.success and "duplicateContactLink" in str(result.raw_response):
            result = self.get_address(client)
            if result.success:
                conn_link = result.data.get("contactLink", {}).get("connLinkContact", {})
                result.data = {
                    "full_link": conn_link.get("connFullLink", ""),
                    "short_link": conn_link.get("connShortLink", ""),
                }
        elif result.success:
            conn_link = result.data.get("connLinkContact", {})
            result.data = {
                "full_link": conn_link.get("connFullLink", ""),
                "short_link": conn_link.get("connShortLink", ""),
            }
        
        return result


# Singleton
_simplex_service: Optional[SimplexCommandService] = None


def get_simplex_service() -> SimplexCommandService:
    """Gibt die Singleton-Instanz zurück"""
    global _simplex_service
    if _simplex_service is None:
        _simplex_service = SimplexCommandService()
    return _simplex_service
