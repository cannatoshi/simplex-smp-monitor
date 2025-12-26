"""
Management Command: Lauscht auf SimpleX Events für Delivery Receipts
"""

import asyncio
import json
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Lauscht auf SimpleX Events für Delivery Receipts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Event Listener...'))
        
        try:
            asyncio.run(self.listen_all_clients())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopped.'))

    @sync_to_async
    def get_running_clients(self):
        from clients.models import SimplexClient
        return list(SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING))

    @sync_to_async
    def update_message_delivered(self, client, text):
        from clients.models import TestMessage
        
        test_msg = TestMessage.objects.filter(
            recipient=client,
            content=text,
            delivery_status=TestMessage.DeliveryStatus.SENT
        ).first()
        
        if test_msg:
            test_msg.mark_delivered()
            return True
        return False

    @sync_to_async
    def update_sender_delivered(self, client, text):
        from clients.models import TestMessage
        
        test_msg = TestMessage.objects.filter(
            sender=client,
            content=text,
            delivery_status=TestMessage.DeliveryStatus.SENT
        ).first()
        
        if test_msg:
            test_msg.mark_delivered()
            return True
        return False

    @sync_to_async
    def increment_received(self, client):
        from clients.models import SimplexClient
        client.messages_received += 1
        client.last_active_at = timezone.now()
        client.save(update_fields=['messages_received', 'last_active_at'])

    async def listen_all_clients(self):
        """Startet Listener für alle laufenden Clients"""
        import websockets
        
        while True:
            clients = await self.get_running_clients()
            
            if not clients:
                self.stdout.write('No running clients. Waiting...')
                await asyncio.sleep(5)
                continue
            
            tasks = []
            for client in clients:
                task = asyncio.create_task(self.listen_client(client))
                tasks.append(task)
            
            self.stdout.write(f'Listening to {len(tasks)} clients...')
            
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            
            for task in pending:
                task.cancel()
            
            await asyncio.sleep(2)

    async def listen_client(self, client):
        """Lauscht auf Events eines einzelnen Clients"""
        import websockets
        
        try:
            async with websockets.connect(client.websocket_url, ping_interval=20) as ws:
                self.stdout.write(f'  ✓ Connected: {client.name} ({client.websocket_url})')
                
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=60)
                        data = json.loads(msg)
                        await self.process_event(client, data)
                    except asyncio.TimeoutError:
                        pass
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error {client.name}: {e}'))
            raise

    async def process_event(self, client, data):
        """Verarbeitet ein SimpleX Event"""
        resp = data.get('resp', {})
        resp_type = resp.get('type', '')
        
        if resp_type == 'newChatItems':
            await self.handle_new_message(client, resp)
        
        elif resp_type == 'chatItemsStatusesUpdated':
            await self.handle_status_update(client, resp)

    async def handle_new_message(self, client, resp):
        """Behandelt eingehende Nachrichten"""
        chat_items = resp.get('chatItems', [])
        
        for item in chat_items:
            chat_item = item.get('chatItem', {})
            content = chat_item.get('content', {})
            
            if content.get('type') != 'rcvMsgContent':
                continue
            
            msg_content = content.get('msgContent', {})
            if msg_content.get('type') != 'text':
                continue
            
            text = msg_content.get('text', '')
            
            chat_info = item.get('chatInfo', {})
            contact = chat_info.get('contact', {})
            sender_name = contact.get('localDisplayName', '')
            
            self.stdout.write(
                self.style.SUCCESS(f'  📨 {client.name} ← {sender_name}: "{text[:30]}..."')
            )
            
            # Update TestMessage
            found = await self.update_message_delivered(client, text)
            if found:
                self.stdout.write(self.style.SUCCESS(f'    ✓✓ Marked as delivered'))
            
            # Update counter
            await self.increment_received(client)

    async def handle_status_update(self, client, resp):
        """Behandelt Status-Updates für gesendete Nachrichten"""
        chat_items = resp.get('chatItems', [])
        
        for item in chat_items:
            chat_item = item.get('chatItem', {})
            meta = chat_item.get('meta', {})
            item_status = meta.get('itemStatus', {})
            status_type = item_status.get('type', '')
            
            if status_type in ['sndRcvd', 'sndRead']:
                content = chat_item.get('content', {})
                msg_content = content.get('msgContent', {})
                text = msg_content.get('text', '') if msg_content else ''
                
                if text:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓✓ {client.name} delivery confirmed: "{text[:30]}..."')
                    )
                    
                    await self.update_sender_delivered(client, text)
