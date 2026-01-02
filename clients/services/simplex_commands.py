"""
SimpleX Chat Command Service

Synchronous service for SimpleX CLI commands via WebSocket.
Called from Django views to interact with SimpleX containers.

Usage:
    from clients.services.simplex_commands import get_simplex_service
    
    svc = get_simplex_service()
    result = svc.send_message(client, "alice", "Hello!", tracking_id="msg_abc123")
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
    """Result of a SimpleX command execution"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    raw_response: Optional[Dict] = None


class SimplexCommandService:
    """
    Synchronous service for SimpleX CLI WebSocket commands.
    
    Provides a clean API for Django views to interact with SimpleX containers
    without having to deal with async/await directly.
    """
    
    def __init__(self):
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def _run_async(self, coro):
        """Run async coroutine synchronously"""
        loop = self._get_loop()
        return loop.run_until_complete(coro)
    
    async def _send_command(self, ws_url: str, command: str, timeout: float = 30.0) -> CommandResult:
        """
        Send command via WebSocket and wait for response.
        
        Args:
            ws_url: WebSocket URL (e.g. ws://localhost:3031)
            command: SimpleX CLI command (e.g. "/contacts", "@alice Hello")
            timeout: Response timeout in seconds
            
        Returns:
            CommandResult with success status and response data
        """
        import websockets
        
        corr_id = str(uuid.uuid4())[:8]
        request = json.dumps({"corrId": corr_id, "cmd": command})
        
        try:
            async with websockets.connect(ws_url, close_timeout=5) as ws:
                # Skip initial events that might be queued
                try:
                    while True:
                        msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                        data = json.loads(msg)
                        if data.get("corrId") == corr_id:
                            break
                except asyncio.TimeoutError:
                    pass
                
                # Send command
                await ws.send(request)
                logger.debug(f"Sent: {request}")
                
                # Wait for response with matching correlation ID
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
                        
                        # Check for error response
                        if resp_type == "chatCmdError":
                            error_info = resp.get("chatError", {})
                            error_type = error_info.get("errorType", {})
                            error_msg = error_type.get("message", str(error_type))
                            return CommandResult(success=False, data={}, error=error_msg, raw_response=data)
                        
                        return CommandResult(success=True, data=resp, raw_response=data)
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            return CommandResult(success=False, data={}, error=str(e))
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    def create_address(self, client) -> CommandResult:
        """
        Create a new invitation link for a client.
        
        Args:
            client: SimplexClient model instance
            
        Returns:
            CommandResult with full_link and short_link in data
        """
        result = self._run_async(self._send_command(client.websocket_url, "/address"))
        
        if result.success:
            conn_link = result.data.get("connLinkContact", {})
            result.data = {
                "full_link": conn_link.get("connFullLink", ""),
                "short_link": conn_link.get("connShortLink", ""),
            }
        return result
    
    def get_address(self, client) -> CommandResult:
        """
        Get the existing address of a client.
        
        Args:
            client: SimplexClient model instance
            
        Returns:
            CommandResult with address data
        """
        return self._run_async(self._send_command(client.websocket_url, "/show_address"))
    
    def connect_via_link(self, client, invitation_link: str) -> CommandResult:
        """
        Connect client to another contact via invitation link.
        
        Args:
            client: SimplexClient model instance
            invitation_link: SimpleX invitation link
            
        Returns:
            CommandResult with connection data
        """
        return self._run_async(self._send_command(client.websocket_url, f"/connect {invitation_link}"))
    
    def send_message(self, client, contact_name: str, message: str, 
                     tracking_id: Optional[str] = None) -> CommandResult:
        """
        Send a message to a contact.
        
        If tracking_id is provided, it will be embedded in the message content
        as a prefix: "[msg_xxxx] actual message". This allows the Event Bridge
        to reliably match delivery receipts to the original message.
        
        Args:
            client: SimplexClient model instance (sender)
            contact_name: Name of the contact to send to
            message: Message content
            tracking_id: Optional tracking ID for reliable delivery tracking
            
        Returns:
            CommandResult with send confirmation
        """
        # Embed tracking ID in message if provided
        if tracking_id:
            full_message = f"[{tracking_id}] {message}"
        else:
            full_message = message
        
        command = f"@{contact_name} {full_message}"
        return self._run_async(self._send_command(client.websocket_url, command))
    
    def get_contacts(self, client) -> CommandResult:
        """
        List all contacts of a client.
        
        Args:
            client: SimplexClient model instance
            
        Returns:
            CommandResult with contacts list
        """
        return self._run_async(self._send_command(client.websocket_url, "/contacts"))
    
    def accept_contact(self, client, contact_name: str) -> CommandResult:
        """
        Accept a pending contact request.
        
        Args:
            client: SimplexClient model instance
            contact_name: Name of the contact to accept
            
        Returns:
            CommandResult with acceptance confirmation
        """
        return self._run_async(self._send_command(client.websocket_url, f"/accept {contact_name}"))
    
    def enable_auto_accept(self, client) -> CommandResult:
        """
        Enable auto-accept for incoming contact requests.
        
        Args:
            client: SimplexClient model instance
            
        Returns:
            CommandResult with confirmation
        """
        return self._run_async(self._send_command(client.websocket_url, "/auto_accept on"))
    
    def create_or_get_address(self, client) -> CommandResult:
        """
        Create a new address or get the existing one.
        
        This is a convenience method that handles the case where
        an address already exists (duplicateContactLink error).
        
        Args:
            client: SimplexClient model instance
            
        Returns:
            CommandResult with full_link and short_link in data
        """
        result = self._run_async(self._send_command(client.websocket_url, "/address"))
        
        # If address already exists, fetch it
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
    
    def delete_contact(self, client, contact_name: str) -> CommandResult:
        """
        Delete a contact.
        
        Args:
            client: SimplexClient model instance
            contact_name: Name of the contact to delete
            
        Returns:
            CommandResult with deletion confirmation
        """
        return self._run_async(self._send_command(client.websocket_url, f"/delete {contact_name}"))
    
    def get_chats(self, client) -> CommandResult:
        """
        Get all chats with recent messages.
        
        Args:
            client: SimplexClient model instance
            
        Returns:
            CommandResult with chats data
        """
        return self._run_async(self._send_command(client.websocket_url, "/chats"))


# =============================================================================
# Singleton Pattern
# =============================================================================

_simplex_service: Optional[SimplexCommandService] = None


def get_simplex_service() -> SimplexCommandService:
    """Get the singleton SimplexCommandService instance"""
    global _simplex_service
    if _simplex_service is None:
        _simplex_service = SimplexCommandService()
    return _simplex_service