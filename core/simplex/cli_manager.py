"""
SimpleX CLI Manager
Manages multiple SimpleX Chat CLI instances for stress testing.
"""
import asyncio
import json
import logging
import time
import uuid
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Callable, Dict, List, Any
from pathlib import Path

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

from .metrics import get_metrics_writer, MetricsWriter

logger = logging.getLogger(__name__)


class ClientStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    CONNECTED = "connected"
    ERROR = "error"
    STOPPING = "stopping"


@dataclass
class MessageTracker:
    """Tracks a message for latency measurement"""
    message_id: str
    sent_at: float
    content: str
    received_at: Optional[float] = None
    
    @property
    def latency_ms(self) -> Optional[float]:
        if self.received_at:
            return (self.received_at - self.sent_at) * 1000
        return None
    
    @property
    def is_received(self) -> bool:
        return self.received_at is not None


@dataclass 
class CLIInstance:
    """Represents a single SimpleX CLI instance"""
    instance_id: str
    port: int
    data_dir: Path
    status: ClientStatus = ClientStatus.STOPPED
    process: Optional[asyncio.subprocess.Process] = None
    websocket: Optional[Any] = None
    pending_messages: Dict[str, MessageTracker] = field(default_factory=dict)
    received_count: int = 0
    sent_count: int = 0
    error_count: int = 0
    
    @property
    def ws_url(self) -> str:
        return f"ws://localhost:{self.port}"


class SimplexCLIManager:
    """
    Manages multiple SimpleX CLI instances for stress testing.
    
    Usage:
        manager = SimplexCLIManager()
        await manager.start_instance("client1", port=5225)
        await manager.start_instance("client2", port=5226)
        
        # Run stress test
        await manager.run_stress_test(
            test_id="test-001",
            duration_seconds=60,
            message_interval=5
        )
        
        await manager.stop_all()
    """
    
    def __init__(
        self,
        cli_path: str = "simplex-chat",
        base_data_dir: str = "/tmp/simplex-test",
        metrics_writer: Optional[MetricsWriter] = None
    ):
        self.cli_path = cli_path
        self.base_data_dir = Path(base_data_dir)
        self.base_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.instances: Dict[str, CLIInstance] = {}
        self.metrics = metrics_writer or get_metrics_writer()
        self._running = False
        self._message_handlers: List[Callable] = []
        
    async def start_instance(
        self,
        instance_id: str,
        port: int,
        servers: Optional[List[str]] = None
    ) -> CLIInstance:
        """Start a new CLI instance"""
        if not WEBSOCKETS_AVAILABLE:
            raise RuntimeError("websockets library not installed")
        
        if instance_id in self.instances:
            raise ValueError(f"Instance {instance_id} already exists")
        
        data_dir = self.base_data_dir / instance_id
        data_dir.mkdir(parents=True, exist_ok=True)
        
        instance = CLIInstance(
            instance_id=instance_id,
            port=port,
            data_dir=data_dir
        )
        instance.status = ClientStatus.STARTING
        self.instances[instance_id] = instance
        
        # Build command
        cmd = [
            self.cli_path,
            "-d", str(data_dir),
            "-p", str(port)
        ]
        
        # Add servers if specified
        if servers:
            for server in servers:
                cmd.extend(["-s", server])
        
        try:
            # Start the CLI process
            instance.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True
            )
            
            logger.info(f"Started CLI instance {instance_id} on port {port}, PID: {instance.process.pid}")
            
            # Wait a bit for the WebSocket server to start
            await asyncio.sleep(2)
            
            # Connect via WebSocket
            await self._connect_websocket(instance)
            
            instance.status = ClientStatus.RUNNING
            
            # Start message listener
            asyncio.create_task(self._listen_for_messages(instance))
            
            return instance
            
        except Exception as e:
            instance.status = ClientStatus.ERROR
            logger.error(f"Failed to start instance {instance_id}: {e}")
            raise
    
    async def _connect_websocket(self, instance: CLIInstance, retries: int = 5):
        """Connect to CLI WebSocket API"""
        for attempt in range(retries):
            try:
                instance.websocket = await websockets.connect(
                    instance.ws_url,
                    ping_interval=20,
                    ping_timeout=10
                )
                instance.status = ClientStatus.CONNECTED
                logger.info(f"WebSocket connected to {instance.instance_id}")
                return
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                else:
                    raise RuntimeError(f"Failed to connect WebSocket after {retries} attempts: {e}")
    
    async def _listen_for_messages(self, instance: CLIInstance):
        """Listen for incoming messages from CLI"""
        if not instance.websocket:
            return
            
        try:
            async for message in instance.websocket:
                await self._handle_message(instance, message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"WebSocket closed for {instance.instance_id}")
            instance.status = ClientStatus.STOPPED
        except Exception as e:
            logger.error(f"Error in message listener for {instance.instance_id}: {e}")
            instance.status = ClientStatus.ERROR
    
    async def _handle_message(self, instance: CLIInstance, raw_message: str):
        """Process incoming message from CLI"""
        try:
            data = json.loads(raw_message)
            resp = data.get("resp", {})
            resp_type = resp.get("type", "")
            corr_id = data.get("corrId")
            
            # Check if this is a response to a sent message
            if corr_id and corr_id in instance.pending_messages:
                tracker = instance.pending_messages[corr_id]
                tracker.received_at = time.time()
                instance.received_count += 1
                
                # Log to metrics
                if self.metrics:
                    self.metrics.write_latency(
                        test_id=getattr(self, '_current_test_id', 'unknown'),
                        client_id=instance.instance_id,
                        latency_ms=tracker.latency_ms,
                        server="unknown"  # TODO: Extract from message
                    )
                
                logger.debug(f"Message {corr_id} received, latency: {tracker.latency_ms:.2f}ms")
            
            # Notify handlers
            for handler in self._message_handlers:
                try:
                    await handler(instance.instance_id, data)
                except Exception as e:
                    logger.error(f"Handler error: {e}")
                    
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from {instance.instance_id}: {raw_message[:100]}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def send_command(
        self,
        instance_id: str,
        command: str,
        track_latency: bool = False
    ) -> Optional[str]:
        """Send a command to CLI instance"""
        instance = self.instances.get(instance_id)
        if not instance or not instance.websocket:
            raise ValueError(f"Instance {instance_id} not connected")
        
        corr_id = str(uuid.uuid4())[:8]
        
        msg = json.dumps({
            "corrId": corr_id,
            "cmd": command
        })
        
        if track_latency:
            instance.pending_messages[corr_id] = MessageTracker(
                message_id=corr_id,
                sent_at=time.time(),
                content=command
            )
            instance.sent_count += 1
        
        await instance.websocket.send(msg)
        return corr_id
    
    async def send_message(
        self,
        instance_id: str,
        contact: str,
        message: str
    ) -> str:
        """Send a chat message to a contact"""
        command = f"@{contact} {message}"
        return await self.send_command(instance_id, command, track_latency=True)
    
    async def stop_instance(self, instance_id: str):
        """Stop a CLI instance"""
        instance = self.instances.get(instance_id)
        if not instance:
            return
        
        instance.status = ClientStatus.STOPPING
        
        # Close WebSocket
        if instance.websocket:
            await instance.websocket.close()
        
        # Terminate process
        if instance.process:
            try:
                instance.process.terminate()
                await asyncio.wait_for(instance.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                instance.process.kill()
                await instance.process.wait()
        
        instance.status = ClientStatus.STOPPED
        logger.info(f"Stopped instance {instance_id}")
    
    async def stop_all(self):
        """Stop all CLI instances"""
        self._running = False
        for instance_id in list(self.instances.keys()):
            await self.stop_instance(instance_id)
        self.instances.clear()
    
    def add_message_handler(self, handler: Callable):
        """Add a handler for incoming messages"""
        self._message_handlers.append(handler)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        total_sent = sum(i.sent_count for i in self.instances.values())
        total_received = sum(i.received_count for i in self.instances.values())
        total_errors = sum(i.error_count for i in self.instances.values())
        
        # Calculate latencies
        all_latencies = []
        for instance in self.instances.values():
            for tracker in instance.pending_messages.values():
                if tracker.latency_ms is not None:
                    all_latencies.append(tracker.latency_ms)
        
        return {
            "active_instances": len([i for i in self.instances.values() if i.status == ClientStatus.CONNECTED]),
            "total_instances": len(self.instances),
            "messages_sent": total_sent,
            "messages_received": total_received,
            "errors": total_errors,
            "delivery_rate": (total_received / total_sent * 100) if total_sent > 0 else 0,
            "avg_latency_ms": sum(all_latencies) / len(all_latencies) if all_latencies else None,
            "min_latency_ms": min(all_latencies) if all_latencies else None,
            "max_latency_ms": max(all_latencies) if all_latencies else None,
        }
    
    async def run_stress_test(
        self,
        test_id: str,
        duration_seconds: int = 60,
        message_interval: float = 5.0,
        on_progress: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run a stress test across all connected instances.
        
        Args:
            test_id: Unique test identifier
            duration_seconds: How long to run the test
            message_interval: Seconds between messages per client
            on_progress: Callback function(stats_dict) called periodically
        
        Returns:
            Final test statistics
        """
        self._current_test_id = test_id
        self._running = True
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # Get connected instances
        connected = [i for i in self.instances.values() if i.status == ClientStatus.CONNECTED]
        if len(connected) < 2:
            raise ValueError("Need at least 2 connected instances for stress test")
        
        logger.info(f"Starting stress test {test_id} with {len(connected)} clients for {duration_seconds}s")
        
        # Reset counters
        for instance in connected:
            instance.sent_count = 0
            instance.received_count = 0
            instance.error_count = 0
            instance.pending_messages.clear()
        
        # Create message tasks for each instance
        async def send_messages(instance: CLIInstance, targets: List[CLIInstance]):
            """Send messages from one instance to others"""
            while self._running and time.time() < end_time:
                for target in targets:
                    if not self._running:
                        break
                    try:
                        msg_content = f"Test message {uuid.uuid4().hex[:8]} at {time.time()}"
                        # In real scenario, we'd send to the target's contact address
                        # For now, we just track the message
                        corr_id = await self.send_command(
                            instance.instance_id,
                            f"# Test: {msg_content}",  # Just echo to self for testing
                            track_latency=True
                        )
                        
                        if self.metrics:
                            self.metrics.write_message_sent(
                                test_id=test_id,
                                client_id=instance.instance_id,
                                server="test-server",
                                message_id=corr_id
                            )
                            
                    except Exception as e:
                        instance.error_count += 1
                        logger.error(f"Send error from {instance.instance_id}: {e}")
                        
                await asyncio.sleep(message_interval)
        
        # Start sending from each instance to all others
        tasks = []
        for i, sender in enumerate(connected):
            targets = [c for j, c in enumerate(connected) if i != j]
            tasks.append(asyncio.create_task(send_messages(sender, targets)))
        
        # Progress reporting
        async def report_progress():
            while self._running and time.time() < end_time:
                stats = self.get_stats()
                stats["elapsed_seconds"] = int(time.time() - start_time)
                stats["remaining_seconds"] = int(end_time - time.time())
                
                if self.metrics:
                    self.metrics.write_test_status(
                        test_id=test_id,
                        status="running",
                        active_clients=stats["active_instances"],
                        messages_sent=stats["messages_sent"],
                        messages_received=stats["messages_received"],
                        delivery_rate=stats["delivery_rate"],
                        avg_latency_ms=stats.get("avg_latency_ms")
                    )
                
                if on_progress:
                    try:
                        await on_progress(stats)
                    except Exception as e:
                        logger.error(f"Progress callback error: {e}")
                
                await asyncio.sleep(2)
        
        tasks.append(asyncio.create_task(report_progress()))
        
        # Wait for test duration
        try:
            await asyncio.sleep(duration_seconds)
        finally:
            self._running = False
            
        # Cancel remaining tasks
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Final stats
        final_stats = self.get_stats()
        final_stats["test_id"] = test_id
        final_stats["duration_seconds"] = duration_seconds
        final_stats["completed_at"] = datetime.now().isoformat()
        
        if self.metrics:
            self.metrics.write_test_status(
                test_id=test_id,
                status="completed",
                active_clients=final_stats["active_instances"],
                messages_sent=final_stats["messages_sent"],
                messages_received=final_stats["messages_received"],
                delivery_rate=final_stats["delivery_rate"],
                avg_latency_ms=final_stats.get("avg_latency_ms")
            )
        
        logger.info(f"Test {test_id} completed: {final_stats}")
        return final_stats


# Convenience function for Django integration
async def run_test(
    test_id: str,
    servers: List[str],
    num_clients: int = 2,
    duration_seconds: int = 60,
    message_interval: float = 5.0,
    on_progress: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    High-level function to run a complete stress test.
    Creates CLI instances, runs test, and cleans up.
    """
    manager = SimplexCLIManager()
    
    try:
        # Start clients
        base_port = int(os.environ.get('SIMPLEX_CLI_BASE_PORT', 5225))
        for i in range(num_clients):
            await manager.start_instance(
                instance_id=f"client-{i}",
                port=base_port + i,
                servers=servers
            )
        
        # Run test
        results = await manager.run_stress_test(
            test_id=test_id,
            duration_seconds=duration_seconds,
            message_interval=message_interval,
            on_progress=on_progress
        )
        
        return results
        
    finally:
        await manager.stop_all()
