"""
SimpleX Event Bridge - Polling Version

Da SimpleX CLI v6.x keine Events automatisch pusht,
pollen wir regelmäßig nach neuen Nachrichten.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Optional, List
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class SimplexEventBridge:
    """
    Bridge zwischen SimpleX CLI Containern und Django Channels.
    Verwendet Polling für Message Status Updates.
    """
    
    def __init__(self):
        self.channel_layer = None
        self.running = False
        self.poll_interval = 10
        self.connected_clients = 0
    
    async def start(self):
        """Startet den Event Bridge"""
        self.channel_layer = get_channel_layer()
        self.running = True
        logger.info("🚀 SimplexEventBridge starting (polling mode)...")
        
        while self.running:
            try:
                await self._poll_all_clients()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Bridge error: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stoppt den Event Bridge"""
        self.running = False
        logger.info("SimplexEventBridge stopped")
    
    @sync_to_async
    def _get_running_clients(self) -> List[dict]:
        """Holt alle laufenden Clients aus der DB"""
        from clients.models import SimplexClient
        return list(
            SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING)
            .values('id', 'slug', 'name', 'websocket_port')
        )
    
    @sync_to_async
    def _get_pending_messages(self) -> List[dict]:
        """Holt alle Nachrichten die noch nicht delivered sind"""
        from clients.models import TestMessage
        
        messages = TestMessage.objects.filter(
            delivery_status__in=[
                TestMessage.DeliveryStatus.SENDING,
                TestMessage.DeliveryStatus.SENT
            ]
        ).select_related('sender', 'recipient')
        
        result = []
        for msg in messages:
            result.append({
                'id': msg.id,
                'content': msg.content,
                'sender_slug': msg.sender.slug if msg.sender else None,
                'recipient_slug': msg.recipient.slug if msg.recipient else None,
                'sender_port': msg.sender.websocket_port if msg.sender else None,
                'recipient_port': msg.recipient.websocket_port if msg.recipient else None,
                'delivery_status': str(msg.delivery_status),
                'sent_at': msg.sent_at,
            })
        return result
    
    @sync_to_async
    def _mark_message_delivered(self, message_id) -> Optional[int]:
        """Markiert eine Nachricht als delivered"""
        from clients.models import TestMessage
        
        try:
            msg = TestMessage.objects.get(id=message_id)
            msg.delivery_status = TestMessage.DeliveryStatus.DELIVERED
            msg.client_received_at = timezone.now()
            if msg.sent_at:
                msg.total_latency_ms = int(
                    (msg.client_received_at - msg.sent_at).total_seconds() * 1000
                )
            msg.save()
            return msg.total_latency_ms
        except TestMessage.DoesNotExist:
            return None
    
    @sync_to_async
    def _update_client_stats(self, slug: str, received_increment: int = 0):
        """Updated Client Statistics"""
        from clients.models import SimplexClient
        from django.db.models import F
        
        SimplexClient.objects.filter(slug=slug).update(
            messages_received=F('messages_received') + received_increment,
            last_active_at=timezone.now()
        )
    
    @sync_to_async
    def _get_client_stats(self, slug: str) -> Optional[dict]:
        """Holt aktuelle Client Stats"""
        from clients.models import SimplexClient
        return SimplexClient.objects.filter(slug=slug).values(
            'messages_sent', 'messages_received'
        ).first()
    
    async def _poll_all_clients(self):
        """Pollt alle laufenden Clients für Updates"""
        clients = await self._get_running_clients()
        pending_messages = await self._get_pending_messages()
        
        # Update connected clients count
        self.connected_clients = len(clients)
        
        # Sende Bridge Status an Browser
        if self.channel_layer:
            try:
                await self.channel_layer.group_send(
                    "clients_all",
                    {
                        "type": "bridge_status",
                        "connected_clients": self.connected_clients,
                    }
                )
            except Exception as e:
                logger.debug(f"Could not send bridge status: {e}")
        
        if not clients:
            return
        
        # Auch ohne pending messages die Clients pollen (für Stats)
        for client in clients:
            try:
                await self._poll_client(client, pending_messages or [])
            except Exception as e:
                logger.debug(f"Poll error {client['name']}: {e}")
    
    async def _poll_all_clients(self):
        """Pollt alle laufenden Clients für Updates"""
        clients = await self._get_running_clients()
        pending_messages = await self._get_pending_messages()
        
        # Update connected clients count
        self.connected_clients = len(clients)
        
        # Sende Bridge Status an Browser
        if self.channel_layer:
            try:
                await self.channel_layer.group_send(
                    "clients_all",
                    {
                        "type": "bridge_status",
                        "connected_clients": self.connected_clients,
                    }
                )
            except Exception as e:
                logger.debug(f"Could not send bridge status: {e}")
        
        # NUR pollen wenn pending messages existieren!
        if not clients or not pending_messages:
            return  # <-- Hier aufhören, kein Polling nötig
        
        # Ab hier nur wenn es was zu tracken gibt
        for client in clients:
            try:
                await self._poll_client(client, pending_messages)
            except Exception as e:
                logger.debug(f"Poll error {client['name']}: {e}")
    
    async def _send_command(self, ws, cmd: str) -> Optional[dict]:
        """Sendet einen Command und wartet auf Antwort"""
        corr_id = str(uuid.uuid4())[:8]
        request = json.dumps({"corrId": corr_id, "cmd": cmd})
        
        await ws.send(request)
        
        try:
            for _ in range(10):
                msg = await asyncio.wait_for(ws.recv(), timeout=2)
                data = json.loads(msg)
                if data.get("corrId") == corr_id:
                    return data.get("resp", {})
        except asyncio.TimeoutError:
            pass
        return None
    
    async def _check_message_received(self, chats_data: dict, content: str) -> bool:
        """Prüft ob eine Nachricht beim Empfänger angekommen ist"""
        if chats_data.get("type") != "chats":
            return False
        
        for chat_data in chats_data.get("chats", []):
            chat_items = chat_data.get("chatItems", [])
            
            for item in chat_items:
                chat_item = item if isinstance(item, dict) else {}
                item_content = chat_item.get("content", {})
                msg_content = item_content.get("msgContent", {})
                
                if msg_content.get("type") == "text":
                    text = msg_content.get("text", "")
                    if text == content:
                        return True
        
        return False
    
    async def _check_delivery_confirmed(self, chats_data: dict, content: str) -> bool:
        """Prüft ob eine gesendete Nachricht als delivered bestätigt wurde"""
        if chats_data.get("type") != "chats":
            return False
        
        for chat_data in chats_data.get("chats", []):
            chat_items = chat_data.get("chatItems", [])
            
            for item in chat_items:
                chat_item = item if isinstance(item, dict) else {}
                item_content = chat_item.get("content", {})
                msg_content = item_content.get("msgContent", {})
                
                if msg_content.get("type") == "text":
                    text = msg_content.get("text", "")
                    if text == content:
                        meta = chat_item.get("meta", {})
                        item_status = meta.get("itemStatus", {})
                        status_type = item_status.get("type", "")
                        
                        if status_type in ["sndRcvd", "sndRead"]:
                            return True
        
        return False
    
    async def _push_stats_update(self, slug: str):
        """Pusht Stats Update an Browser"""
        client = await self._get_client_stats(slug)
        
        if client:
            await self.channel_layer.group_send(
                "clients_all",
                {
                    "type": "client_stats",
                    "client_slug": slug,
                    "messages_sent": client['messages_sent'],
                    "messages_received": client['messages_received'],
                }
            )


_bridge: SimplexEventBridge = None


def get_event_bridge() -> SimplexEventBridge:
    global _bridge
    if _bridge is None:
        _bridge = SimplexEventBridge()
    return _bridge


async def start_event_bridge():
    bridge = get_event_bridge()
    await bridge.start()


async def stop_event_bridge():
    global _bridge
    if _bridge:
        await _bridge.stop()
        _bridge = None