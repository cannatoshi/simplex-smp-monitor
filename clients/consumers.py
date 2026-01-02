"""
WebSocket Consumers for real-time client updates
"""

import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class ClientUpdateConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket Consumer für die Client-Liste.
    Empfängt Updates für alle Clients.
    """
    
    async def connect(self):
        self.group_name = "clients_all"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name}")
    
    async def receive_json(self, content):
        """Empfängt Commands vom Browser"""
        action = content.get("action")
        
        if action == "ping":
            await self.send_json({"type": "pong"})
    
    # === Event Handlers (from Channel Layer) ===
    
    async def bridge_status(self, event):
        """Bridge Status Update - connected clients count"""
        await self.send_json({
            "type": "bridge_status",
            "connected_clients": event["connected_clients"],
        })
    
    async def client_status(self, event):
        """Client Status Update"""
        await self.send_json({
            "type": "client_status",
            "client_slug": event["client_slug"],
            "status": event["status"],
            "container_id": event.get("container_id"),
        })
    
    async def client_stats(self, event):
        """Client Statistics Update"""
        await self.send_json({
            "type": "client_stats",
            "client_slug": event["client_slug"],
            "messages_sent": event["messages_sent"],
            "messages_received": event["messages_received"],
        })
    
    async def message_status(self, event):
        """Message Delivery Status Update"""
        await self.send_json({
            "type": "message_status",
            "message_id": event["message_id"],
            "status": event["status"],
            "latency_ms": event.get("latency_ms"),
        })
    
    async def new_message(self, event):
        """Neue Nachricht empfangen"""
        await self.send_json({
            "type": "new_message",
            "client_slug": event["client_slug"],
            "sender": event["sender"],
            "content": event["content"],
            "timestamp": event["timestamp"],
        })

    async def connection_created(self, event):
        """Neue Verbindung erstellt"""
        await self.send_json({
            "type": "connection_created",
            "client_a_slug": event["client_a_slug"],
            "client_b_slug": event["client_b_slug"],
            "client_a_name": event["client_a_name"],
            "client_b_name": event["client_b_name"],
            "contact_name_on_a": event["contact_name_on_a"],
            "contact_name_on_b": event["contact_name_on_b"],
            "status": event["status"],
        })

    async def connection_deleted(self, event):
        """Verbindung gelöscht"""
        await self.send_json({
            "type": "connection_deleted",
            "connection_id": event["connection_id"],
            "client_a_slug": event["client_a_slug"],
        })

    async def test_progress(self, event):
        """Test run progress update"""
        await self.send_json({
            "type": "test_progress",
            "test_run_id": event["test_run_id"],
            "messages_sent": event["messages_sent"],
            "messages_delivered": event["messages_delivered"],
            "messages_failed": event["messages_failed"],
            "progress_percent": event["progress_percent"],
        })


class ClientDetailConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket Consumer für Client Detail Page.
    Empfängt Updates nur für einen spezifischen Client.
    """
    
    async def connect(self):
        self.client_slug = self.scope['url_route']['kwargs']['client_slug']
        self.group_name = f"client_{self.client_slug}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        # Auch zur globalen Gruppe für übergreifende Updates
        await self.channel_layer.group_add(
            "clients_all",
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connected to client: {self.client_slug}")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            "clients_all",
            self.channel_name
        )
    
    async def receive_json(self, content):
        action = content.get("action")
        
        if action == "ping":
            await self.send_json({"type": "pong"})
    
    # Event Handlers - same as ClientUpdateConsumer
    
    async def bridge_status(self, event):
        """Bridge Status Update"""
        await self.send_json({
            "type": "bridge_status",
            "connected_clients": event["connected_clients"],
        })
    
    async def client_status(self, event):
        await self.send_json({
            "type": "client_status",
            "client_slug": event["client_slug"],
            "status": event["status"],
        })
    
    async def client_stats(self, event):
        await self.send_json({
            "type": "client_stats",
            "client_slug": event["client_slug"],
            "messages_sent": event["messages_sent"],
            "messages_received": event["messages_received"],
        })
    
    async def message_status(self, event):
        await self.send_json({
            "type": "message_status",
            "message_id": event["message_id"],
            "status": event["status"],
            "latency_ms": event.get("latency_ms"),
        })
    
    async def new_message(self, event):
        await self.send_json({
            "type": "new_message",
            "client_slug": event["client_slug"],
            "sender": event["sender"],
            "content": event["content"],
            "timestamp": event["timestamp"],
        })
    
    async def container_log(self, event):
        """Container Log Line"""
        await self.send_json({
            "type": "container_log",
            "line": event["line"],
        })

    async def connection_created(self, event):
        """Neue Verbindung erstellt"""
        await self.send_json({
            "type": "connection_created",
            "client_a_slug": event["client_a_slug"],
            "client_b_slug": event["client_b_slug"],
            "client_a_name": event["client_a_name"],
            "client_b_name": event["client_b_name"],
            "contact_name_on_a": event["contact_name_on_a"],
            "contact_name_on_b": event["contact_name_on_b"],
            "status": event["status"],
        })

    async def connection_deleted(self, event):
        """Verbindung gelöscht"""
        await self.send_json({
            "type": "connection_deleted",
            "connection_id": event["connection_id"],
            "client_a_slug": event["client_a_slug"],
        })

    async def test_progress(self, event):
        """Test run progress update"""
        await self.send_json({
            "type": "test_progress",
            "test_run_id": event["test_run_id"],
            "messages_sent": event["messages_sent"],
            "messages_delivered": event["messages_delivered"],
            "messages_failed": event["messages_failed"],
            "progress_percent": event["progress_percent"],
        })

    