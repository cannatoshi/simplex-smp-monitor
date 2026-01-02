"""
Test Runner Service

Executes test runs with configurable parameters.
"""

import asyncio
import logging
import random
import string
import threading
from datetime import datetime
from typing import Optional, List
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

_active_runners = {}


class TestRunner:
    def __init__(self, test_run):
        self.test_run = test_run
        self.cancelled = False
        self._thread: Optional[threading.Thread] = None
    
    @classmethod
    def cancel(cls, test_run_id: str):
        runner = _active_runners.get(str(test_run_id))
        if runner:
            runner.cancelled = True
            logger.info(f"Test run {test_run_id} cancelled")
    
    def start_async(self):
        self._thread = threading.Thread(target=self._run_sync, daemon=True)
        self._thread.start()
        _active_runners[str(self.test_run.id)] = self
    
    def _run_sync(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run())
        finally:
            loop.close()
            _active_runners.pop(str(self.test_run.id), None)
    
    async def run(self):
        from .simplex_commands import SimplexCommandService
        
        test_run = self.test_run
        logger.info(f"Starting test run: {test_run.name} ({test_run.message_count} messages)")
        
        # Pre-load sender
        sender = await self._get_sender()
        
        # Get available recipients
        recipients = await self._get_recipients()
        if not recipients:
            await self._update_status('failed')
            logger.error(f"Test run {test_run.name}: No recipients available")
            return
        
        logger.info(f"Test run {test_run.name}: {len(recipients)} recipients available")
        
        recipient_iter = self._create_recipient_iterator(recipients)
        
        for i in range(test_run.message_count):
            if self.cancelled:
                logger.info(f"Test run {test_run.name} cancelled at message {i}")
                break
            
            recipient = next(recipient_iter)
            connection = await self._get_connection(sender, recipient)
            
            if not connection:
                logger.warning(f"No connection to {recipient.name}, skipping")
                continue
            
            content = self._generate_message(i)
            tracking_id = f"test_{test_run.id.hex[:8]}_{i:04d}"
            contact_name = await self._get_contact_name(connection, sender)
            
            try:
                message = await self._create_message(
                    connection, sender, recipient, content, tracking_id
                )
                
                # Run in separate thread to avoid event loop conflict
                result = await sync_to_async(self._send_message_sync)(sender, contact_name, content, tracking_id)
                
                if result.success:
                    await self._update_message_status(message, 'sent')
                    await self._increment_sent()
                    logger.info(f"Test message {i+1}/{test_run.message_count} sent to {recipient.name}")
                else:
                    await self._update_message_status(message, 'failed')
                    await self._increment_failed()
                    logger.warning(f"Test message {i+1} failed: {result.error}")
                
                await self._push_progress_update()
                
            except Exception as e:
                logger.error(f"Error sending message {i}: {e}")
                await self._increment_failed()
            
            if i < test_run.message_count - 1:
                await asyncio.sleep(test_run.interval_ms / 1000)
        
        await self._wait_for_deliveries(timeout=30)
        await self._calculate_results()
        
        if not self.cancelled:
            await self._update_status('completed')
        
        logger.info(f"Test run {test_run.name} completed")
    
    @sync_to_async
    def _get_sender(self):
        """Pre-load sender from database"""
        self.test_run.refresh_from_db()
        return self.test_run.sender
    
    @sync_to_async
    def _get_recipients(self) -> List:
        from ..models import ClientConnection
        
        test_run = self.test_run
        test_run.refresh_from_db()
        sender = test_run.sender
        
        if test_run.recipient_mode == 'selected':
            return list(test_run.selected_recipients.all())
        
        connections = ClientConnection.objects.filter(
            client_a=sender,
            status='connected'
        ).select_related('client_b')
        
        recipients = [c.client_b for c in connections]
        
        connections_reverse = ClientConnection.objects.filter(
            client_b=sender,
            status='connected'
        ).select_related('client_a')
        
        recipients.extend([c.client_a for c in connections_reverse])
        
        seen = set()
        unique = []
        for r in recipients:
            if r.id not in seen:
                seen.add(r.id)
                unique.append(r)
        
        return unique
    
    @sync_to_async
    def _get_connection(self, sender, recipient):
        from ..models import ClientConnection
        
        connection = ClientConnection.objects.filter(
            client_a=sender,
            client_b=recipient,
            status='connected'
        ).first()
        
        if not connection:
            connection = ClientConnection.objects.filter(
                client_a=recipient,
                client_b=sender,
                status='connected'
            ).first()
        
        return connection
    
    @sync_to_async
    def _get_contact_name(self, connection, sender):
        if connection.client_a_id == sender.id:
            return connection.contact_name_on_a
        return connection.contact_name_on_b
    
    @sync_to_async
    def _create_message(self, connection, sender, recipient, content, tracking_id):
        from ..models import TestMessage
        
        return TestMessage.objects.create(
            connection=connection,
            sender=sender,
            recipient=recipient,
            content=f"[{tracking_id}] {content}",
            tracking_id=tracking_id,
            delivery_status='sending',
            sent_at=timezone.now(),
        )
    
    @sync_to_async
    def _update_message_status(self, message, status):
        message.delivery_status = status
        message.save(update_fields=['delivery_status'])
    
    @sync_to_async
    def _increment_sent(self):
        self.test_run.refresh_from_db()
        self.test_run.messages_sent += 1
        self.test_run.save(update_fields=['messages_sent'])
    
    @sync_to_async
    def _increment_failed(self):
        self.test_run.refresh_from_db()
        self.test_run.messages_failed += 1
        self.test_run.save(update_fields=['messages_failed'])
    
    @sync_to_async
    def _update_status(self, status):
        self.test_run.refresh_from_db()
        self.test_run.status = status
        if status in ['completed', 'failed', 'cancelled']:
            self.test_run.completed_at = timezone.now()
        self.test_run.save()
    

    def _send_message_sync(self, sender, contact_name, content, tracking_id):
        """Send message synchronously in separate thread"""
        from .simplex_commands import SimplexCommandService
        svc = SimplexCommandService()
        return svc.send_message(sender, contact_name, content, tracking_id=tracking_id)
    def _create_recipient_iterator(self, recipients: List):
        mode = self.test_run.recipient_mode
        
        if mode == 'all':
            def all_iter():
                while True:
                    for r in recipients:
                        yield r
            return all_iter()
        
        elif mode == 'random':
            def random_iter():
                while True:
                    yield random.choice(recipients)
            return random_iter()
        
        else:
            def rr_iter():
                i = 0
                while True:
                    yield recipients[i % len(recipients)]
                    i += 1
            return rr_iter()
    
    def _generate_message(self, index: int) -> str:
        size = self.test_run.message_size
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = f"Test #{index + 1} @ {timestamp}: "
        
        remaining = max(0, size - len(prefix))
        if remaining > 0:
            chars = string.ascii_letters + string.digits + ' '
            filler = ''.join(random.choices(chars, k=remaining))
            return prefix + filler
        
        return prefix[:size]
    
    async def _wait_for_deliveries(self, timeout: int = 30):
        test_id_prefix = f"test_{self.test_run.id.hex[:8]}"
        start = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start < timeout:
            pending = await self._count_pending(test_id_prefix)
            if pending == 0:
                break
            await asyncio.sleep(0.5)
    
    @sync_to_async
    def _count_pending(self, test_id_prefix):
        from ..models import TestMessage
        return TestMessage.objects.filter(
            tracking_id__startswith=test_id_prefix,
            delivery_status__in=['sending', 'sent']
        ).count()
    
    @sync_to_async
    def _calculate_results(self):
        from ..models import TestMessage
        from django.db.models import Avg, Min, Max
        
        test_run = self.test_run
        test_run.refresh_from_db()
        test_id_prefix = f"test_{test_run.id.hex[:8]}"
        
        messages = TestMessage.objects.filter(
            tracking_id__startswith=test_id_prefix
        )
        
        delivered = messages.filter(delivery_status='delivered').count()
        failed = messages.filter(delivery_status='failed').count()
        
        test_run.messages_delivered = delivered
        test_run.messages_failed = failed
        
        stats = messages.filter(
            delivery_status='delivered',
            total_latency_ms__isnull=False
        ).aggregate(
            avg=Avg('total_latency_ms'),
            min=Min('total_latency_ms'),
            max=Max('total_latency_ms')
        )
        
        test_run.avg_latency_ms = stats['avg']
        test_run.min_latency_ms = stats['min']
        test_run.max_latency_ms = stats['max']
        
        total = test_run.messages_sent
        if total > 0:
            test_run.success_rate = (delivered / total) * 100
        
        test_run.save()
    
    async def _push_progress_update(self):
        try:
            from channels.layers import get_channel_layer
            
            await sync_to_async(self.test_run.refresh_from_db)()
            channel_layer = get_channel_layer()
            if channel_layer:
                await channel_layer.group_send(
                    "clients_all",
                    {
                        "type": "test_progress",
                        "test_run_id": str(self.test_run.id),
                        "messages_sent": self.test_run.messages_sent,
                        "messages_delivered": self.test_run.messages_delivered,
                        "messages_failed": self.test_run.messages_failed,
                        "progress_percent": self.test_run.progress_percent,
                    }
                )
        except Exception as e:
            logger.debug(f"Could not push progress update: {e}")
