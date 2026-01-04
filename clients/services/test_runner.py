"""
SimpleX SMP Monitor by cannatoshi
GitHub: https://github.com/cannatoshi/simplex-smp-monitor
Licensed under AGPL-3.0

Test Runner Service

Executes test runs with configurable parameters.
Features:
- Smart interval adjustment based on network latency
- Backpressure handling for slow networks (Tor)
- Detailed progress tracking with real-time WebSocket updates
- Three latency measurements: send, delivery, total
- Graceful error handling with clear status messages
"""

import asyncio
import logging
import random
import string
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
from collections import deque
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

# Global registry of active test runners
_active_runners: Dict[str, 'TestRunner'] = {}


class TestRunnerError(Exception):
    """Custom exception for test runner errors"""
    pass


class TestRunner:
    """
    Async test runner with smart interval management.
    
    Handles the complexity of:
    - Async message sending in sync Django context
    - Tor latency compensation
    - Real-time progress updates via WebSocket
    - Graceful cancellation and error recovery
    """
    
    # Minimum safe interval to prevent overload
    MIN_SAFE_INTERVAL_MS = 200
    
    # Maximum pending messages before backpressure kicks in
    MAX_PENDING_MESSAGES = 5
    
    # Timeout for waiting on deliveries
    DELIVERY_TIMEOUT_S = 60
    
    def __init__(self, test_run):
        self.test_run = test_run
        self.cancelled = False
        self._thread: Optional[threading.Thread] = None
        
        # Latency tracking for smart interval
        self._recent_latencies: deque = deque(maxlen=10)
        self._avg_latency_ms: float = 0
        
        # Progress tracking
        self._pending_messages: Dict[str, datetime] = {}
        self._message_results: List[Dict[str, Any]] = []
        
        # Error tracking
        self._last_error: Optional[str] = None
        self._consecutive_failures: int = 0
        self._max_consecutive_failures: int = 5
    
    @classmethod
    def get_active(cls, test_run_id: str) -> Optional['TestRunner']:
        """Get active runner by test run ID"""
        return _active_runners.get(str(test_run_id))
    
    @classmethod
    def cancel(cls, test_run_id: str) -> bool:
        """Cancel a running test"""
        runner = _active_runners.get(str(test_run_id))
        if runner:
            runner.cancelled = True
            logger.info(f"Test run {test_run_id} cancellation requested")
            return True
        return False
    
    def start_async(self):
        """Start test execution in background thread"""
        self._thread = threading.Thread(target=self._run_sync, daemon=True)
        self._thread.start()
        _active_runners[str(self.test_run.id)] = self
        logger.info(f"Test runner started for {self.test_run.id}")
    
    def _run_sync(self):
        """Synchronous wrapper for async run method"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run())
        except Exception as e:
            logger.exception(f"Test runner fatal error: {e}")
            # Try to mark as failed
            try:
                from ..models import ClientTestRun as TestRun
                TestRun.objects.filter(id=self.test_run.id).update(
                    status='failed',
                    completed_at=timezone.now()
                )
            except Exception:
                pass
        finally:
            loop.close()
            _active_runners.pop(str(self.test_run.id), None)
            logger.info(f"Test runner finished for {self.test_run.id}")
    
    async def run(self):
        """Main test execution loop"""
        test_run = self.test_run
        
        logger.info(f"═══════════════════════════════════════════════")
        logger.info(f"Starting test: {test_run.name}")
        logger.info(f"  Messages: {test_run.message_count}")
        logger.info(f"  Interval: {test_run.interval_ms}ms")
        logger.info(f"  Size: {test_run.message_size} chars")
        logger.info(f"═══════════════════════════════════════════════")
        
        # Update status to running
        await self._update_status('running')
        await self._set_started_at()
        
        # Pre-load sender
        sender = await self._get_sender()
        if not sender:
            await self._fail_test("Sender client not found")
            return
        
        # Check if sender is running
        if sender.status != 'running':
            await self._fail_test(f"Sender client is not running (status: {sender.status})")
            return
        
        # Get available recipients
        recipients = await self._get_recipients()
        if not recipients:
            await self._fail_test("No connected recipients available")
            return
        
        logger.info(f"Found {len(recipients)} recipients: {[r.name for r in recipients]}")
        
        # Calculate effective interval (respects minimum safe interval)
        effective_interval = self._calculate_effective_interval(test_run.interval_ms)
        
        # Log if interval was adjusted
        if effective_interval > test_run.interval_ms:
            logger.warning(f"Interval adjusted: {test_run.interval_ms}ms → {effective_interval}ms (minimum safe interval)")
        
        # Create recipient iterator
        recipient_iter = self._create_recipient_iterator(recipients)
        
        # Main send loop
        for i in range(test_run.message_count):
            if self.cancelled:
                logger.info(f"Test cancelled at message {i + 1}/{test_run.message_count}")
                await self._update_status('cancelled')
                break
            
            # Check for too many consecutive failures
            if self._consecutive_failures >= self._max_consecutive_failures:
                await self._fail_test(f"Too many consecutive failures ({self._consecutive_failures})")
                break
            
            # Backpressure: wait if too many messages pending
            await self._apply_backpressure()
            
            # Get next recipient
            recipient = next(recipient_iter)
            connection = await self._get_connection(sender, recipient)
            
            if not connection:
                logger.warning(f"No connection to {recipient.name}, skipping")
                continue
            
            # Generate message content with tracking ID
            tracking_id = f"test_{test_run.id.hex[:8]}_{i:04d}"
            content = self._generate_message(i)
            contact_name = await self._get_contact_name(connection, sender)
            
            # Send message
            success = await self._send_single_message(
                index=i,
                sender=sender,
                recipient=recipient,
                connection=connection,
                contact_name=contact_name,
                content=content,
                tracking_id=tracking_id
            )
            
            if success:
                self._consecutive_failures = 0
            else:
                self._consecutive_failures += 1
            
            # Push progress update
            await self._push_progress_update()
            
            # Smart interval: adjust based on recent latencies
            if i < test_run.message_count - 1:
                actual_interval = self._get_smart_interval(effective_interval)
                await asyncio.sleep(actual_interval / 1000)
        
        # Wait for remaining deliveries
        if not self.cancelled:
            logger.info(f"Waiting for {len(self._pending_messages)} pending deliveries...")
            await self._wait_for_deliveries(timeout=self.DELIVERY_TIMEOUT_S)
        
        # Calculate final results
        await self._calculate_results()
        
        # Update final status
        if not self.cancelled and self.test_run.status != 'failed':
            await self._update_status('completed')
        
        # Final progress update
        await self._push_progress_update()
        
        logger.info(f"═══════════════════════════════════════════════")
        logger.info(f"Test completed: {test_run.name}")
        logger.info(f"  Sent: {self.test_run.messages_sent}")
        logger.info(f"  Delivered: {self.test_run.messages_delivered}")
        logger.info(f"  Failed: {self.test_run.messages_failed}")
        logger.info(f"  Success Rate: {self.test_run.success_rate:.1f}%" if self.test_run.success_rate else "  Success Rate: N/A")
        logger.info(f"═══════════════════════════════════════════════")
    
    async def _send_single_message(
        self,
        index: int,
        sender,
        recipient,
        connection,
        contact_name: str,
        content: str,
        tracking_id: str
    ) -> bool:
        """Send a single message and track it"""
        try:
            # Create message record
            message = await self._create_message(
                connection=connection,
                sender=sender,
                recipient=recipient,
                content=content,
                tracking_id=tracking_id
            )
            
            # Track pending message
            send_time = datetime.now()
            self._pending_messages[tracking_id] = send_time
            
            # Send via SimplexCommandService
            result = await sync_to_async(self._send_message_sync)(
                sender, contact_name, content, tracking_id
            )
            
            if result.success:
                await self._update_message_status(message, 'sent')
                await self._increment_sent()
                logger.info(f"✓ Message {index + 1}/{self.test_run.message_count} sent to {recipient.name}")
                return True
            else:
                await self._update_message_status(message, 'failed', result.error)
                await self._increment_failed()
                self._pending_messages.pop(tracking_id, None)
                logger.warning(f"✗ Message {index + 1} failed: {result.error}")
                self._last_error = result.error
                return False
                
        except Exception as e:
            logger.exception(f"Error sending message {index + 1}: {e}")
            await self._increment_failed()
            self._pending_messages.pop(tracking_id, None)
            self._last_error = str(e)
            return False
    
    def _send_message_sync(self, sender, contact_name: str, content: str, tracking_id: str):
        """Synchronous message send (runs in thread)"""
        from .simplex_commands import SimplexCommandService
        svc = SimplexCommandService()
        return svc.send_message(sender, contact_name, content, tracking_id=tracking_id)
    
    def _calculate_effective_interval(self, base_interval: int) -> int:
        """
        Calculate effective interval.
        
        Note: Tor latency does NOT affect send rate. Send rate is local,
        latency is network. You can send 10 msgs/sec even if each takes 5sec to arrive.
        """
        return max(base_interval, self.MIN_SAFE_INTERVAL_MS)
    
    def _get_smart_interval(self, base_interval: int) -> int:
        """Dynamically adjust interval based on recent latencies"""
        if not self._recent_latencies:
            return base_interval
        
        # Calculate average of recent latencies
        avg = sum(self._recent_latencies) / len(self._recent_latencies)
        self._avg_latency_ms = avg
        
        # If average latency is higher than interval, increase interval
        if avg > base_interval * 0.8:
            adjusted = int(avg * 1.2)
            return min(adjusted, base_interval * 3)  # Cap at 3x base
        
        return base_interval
    
    async def _apply_backpressure(self):
        """Wait if too many messages are pending delivery"""
        wait_count = 0
        while len(self._pending_messages) >= self.MAX_PENDING_MESSAGES:
            if self.cancelled:
                break
            if wait_count == 0:
                logger.info(f"Backpressure: waiting for deliveries ({len(self._pending_messages)} pending)")
            await asyncio.sleep(0.2)
            wait_count += 1
            
            # Update pending count by checking database
            if wait_count % 5 == 0:  # Every second
                await self._refresh_pending_messages()
            
            # Timeout after 30 seconds of backpressure
            if wait_count > 150:
                logger.warning("Backpressure timeout - continuing anyway")
                break
    
    async def _refresh_pending_messages(self):
        """Check which pending messages have been delivered"""
        test_id_prefix = f"test_{self.test_run.id.hex[:8]}"
        delivered = await self._get_delivered_tracking_ids(test_id_prefix)
        
        for tracking_id in list(self._pending_messages.keys()):
            if tracking_id in delivered:
                send_time = self._pending_messages.pop(tracking_id)
                # Calculate latency
                latency_ms = int((datetime.now() - send_time).total_seconds() * 1000)
                self._recent_latencies.append(latency_ms)
    
    @sync_to_async
    def _get_delivered_tracking_ids(self, prefix: str) -> set:
        """Get tracking IDs of delivered messages"""
        from ..models import TestMessage
        return set(
            TestMessage.objects.filter(
                tracking_id__startswith=prefix,
                delivery_status='delivered'
            ).values_list('tracking_id', flat=True)
        )
    
    @sync_to_async
    def _check_tor_status(self, sender) -> bool:
        """Check if sender is using Tor"""
        return sender.use_tor
    
    @sync_to_async
    def _get_sender(self):
        """Get sender client from database"""
        self.test_run.refresh_from_db()
        return self.test_run.sender
    
    @sync_to_async
    def _get_recipients(self) -> List:
        """Get available recipients based on mode"""
        from ..models import ClientConnection
        
        test_run = self.test_run
        test_run.refresh_from_db()
        sender = test_run.sender
        
        if test_run.recipient_mode == 'selected':
            return list(test_run.selected_recipients.filter(status='running'))
        
        # Get all connected clients
        connections = ClientConnection.objects.filter(
            client_a=sender,
            status='connected'
        ).select_related('client_b')
        
        recipients = [c.client_b for c in connections if c.client_b.status == 'running']
        
        # Also check reverse connections
        connections_reverse = ClientConnection.objects.filter(
            client_b=sender,
            status='connected'
        ).select_related('client_a')
        
        recipients.extend([c.client_a for c in connections_reverse if c.client_a.status == 'running'])
        
        # Deduplicate
        seen = set()
        unique = []
        for r in recipients:
            if r.id not in seen:
                seen.add(r.id)
                unique.append(r)
        
        return unique
    
    @sync_to_async
    def _get_connection(self, sender, recipient):
        """Get connection between sender and recipient"""
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
    def _get_contact_name(self, connection, sender) -> str:
        """Get contact name for sending"""
        if connection.client_a_id == sender.id:
            return connection.contact_name_on_a
        return connection.contact_name_on_b
    
    @sync_to_async
    def _create_message(self, connection, sender, recipient, content: str, tracking_id: str):
        """Create message record in database"""
        from ..models import TestMessage
        
        return TestMessage.objects.create(
            connection=connection,
            sender=sender,
            recipient=recipient,
            content=f"[{tracking_id}] {content}",
            tracking_id=tracking_id,
            delivery_status='sending',
            sent_at=timezone.now(),
            test_run=self.test_run,  # Link message to test run for latency aggregation
        )
    
    @sync_to_async
    def _update_message_status(self, message, status: str, error: str = ''):
        """Update message delivery status"""
        message.delivery_status = status
        if error:
            message.error_message = error
        message.save(update_fields=['delivery_status', 'error_message'])
    
    @sync_to_async
    def _increment_sent(self):
        """Increment sent counter"""
        self.test_run.refresh_from_db()
        self.test_run.messages_sent += 1
        self.test_run.save(update_fields=['messages_sent'])
    
    @sync_to_async
    def _increment_failed(self):
        """Increment failed counter"""
        self.test_run.refresh_from_db()
        self.test_run.messages_failed += 1
        self.test_run.save(update_fields=['messages_failed'])
    
    @sync_to_async
    def _update_status(self, status: str):
        """Update test run status"""
        self.test_run.refresh_from_db()
        self.test_run.status = status
        if status in ['completed', 'failed', 'cancelled']:
            self.test_run.completed_at = timezone.now()
        self.test_run.save()
    
    @sync_to_async
    def _set_started_at(self):
        """Set started timestamp"""
        self.test_run.refresh_from_db()
        self.test_run.started_at = timezone.now()
        self.test_run.save(update_fields=['started_at'])
    
    async def _fail_test(self, reason: str):
        """Mark test as failed with reason"""
        logger.error(f"Test failed: {reason}")
        self._last_error = reason
        await self._update_status('failed')
        await self._push_progress_update(error=reason)
    
    def _create_recipient_iterator(self, recipients: List):
        """Create iterator based on recipient mode"""
        mode = self.test_run.recipient_mode
        
        if mode == 'all':
            # Broadcast: cycle through all
            def all_iter():
                while True:
                    for r in recipients:
                        yield r
            return all_iter()
        
        elif mode == 'random':
            # Random selection
            def random_iter():
                while True:
                    yield random.choice(recipients)
            return random_iter()
        
        else:  # round_robin or default
            # Round-robin
            def rr_iter():
                i = 0
                while True:
                    yield recipients[i % len(recipients)]
                    i += 1
            return rr_iter()
    
    def _generate_message(self, index: int) -> str:
        """Generate message content with timestamp"""
        size = self.test_run.message_size
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = f"Test #{index + 1} @ {timestamp}: "
        
        remaining = max(0, size - len(prefix))
        if remaining > 0:
            chars = string.ascii_letters + string.digits + ' '
            filler = ''.join(random.choices(chars, k=remaining))
            return prefix + filler
        
        return prefix[:size]
    
    async def _wait_for_deliveries(self, timeout: int = 60):
        """Wait for all pending messages to be delivered"""
        test_id_prefix = f"test_{self.test_run.id.hex[:8]}"
        start = asyncio.get_event_loop().time()
        last_pending = -1
        
        while asyncio.get_event_loop().time() - start < timeout:
            if self.cancelled:
                break
            
            pending = await self._count_pending(test_id_prefix)
            
            if pending != last_pending:
                logger.info(f"Waiting for deliveries: {pending} pending")
                last_pending = pending
            
            if pending == 0:
                logger.info("All messages delivered!")
                break
            
            await asyncio.sleep(0.5)
            
            # Update delivered count
            await self._refresh_delivered_count()
            await self._push_progress_update()
        
        if await self._count_pending(test_id_prefix) > 0:
            logger.warning(f"Delivery timeout: some messages not confirmed")
    
    @sync_to_async
    def _count_pending(self, test_id_prefix: str) -> int:
        """Count messages still pending delivery"""
        from ..models import TestMessage
        return TestMessage.objects.filter(
            tracking_id__startswith=test_id_prefix,
            delivery_status__in=['sending', 'sent']
        ).count()
    
    @sync_to_async
    def _refresh_delivered_count(self):
        """Update delivered count from database"""
        from ..models import TestMessage
        test_id_prefix = f"test_{self.test_run.id.hex[:8]}"
        
        delivered = TestMessage.objects.filter(
            tracking_id__startswith=test_id_prefix,
            delivery_status='delivered'
        ).count()
        
        self.test_run.refresh_from_db()
        self.test_run.messages_delivered = delivered
        self.test_run.save(update_fields=['messages_delivered'])
    
    @sync_to_async
    def _calculate_results(self):
        """Calculate final test results and latency stats"""
        from ..models import TestMessage
        
        test_run = self.test_run
        test_run.refresh_from_db()
        
        # Count by status from related messages
        messages = test_run.messages.all()
        delivered = messages.filter(delivery_status='delivered').count()
        failed = messages.filter(delivery_status='failed').count()
        
        test_run.messages_delivered = delivered
        test_run.messages_failed = failed
        test_run.save(update_fields=['messages_delivered', 'messages_failed'])
        
        # Calculate and save latency stats
        test_run.update_latency_stats()
    
    async def _push_progress_update(self, error: str = None):
        """Send progress update via WebSocket"""
        try:
            from channels.layers import get_channel_layer
            
            await sync_to_async(self.test_run.refresh_from_db)()
            
            channel_layer = get_channel_layer()
            if not channel_layer:
                return
            
            payload = {
                "type": "test_progress",
                "test_run_id": str(self.test_run.id),
                "status": self.test_run.status,
                "messages_sent": self.test_run.messages_sent,
                "messages_delivered": self.test_run.messages_delivered,
                "messages_failed": self.test_run.messages_failed,
                "progress_percent": self.test_run.progress_percent,
                "avg_latency_ms": self._avg_latency_ms,
            }
            
            if error:
                payload["error"] = error
            
            await channel_layer.group_send("clients_all", payload)
            
        except Exception as e:
            logger.debug(f"Could not push progress update: {e}")