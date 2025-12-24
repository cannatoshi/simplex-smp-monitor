"""
InfluxDB Client for SimpleX Test Suite
Handles writing test metrics to InfluxDB 2.x
"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import influxdb-client, graceful fallback if not installed
try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False
    logger.warning("influxdb-client not installed. Metrics will not be persisted.")


@dataclass
class MetricsConfig:
    """Configuration for InfluxDB connection"""
    url: str = "http://localhost:8086"
    token: str = "simplex-test-suite-token-change-in-production"
    org: str = "simplex"
    bucket: str = "metrics"
    
    @classmethod
    def from_env(cls) -> 'MetricsConfig':
        return cls(
            url=os.environ.get('INFLUXDB_URL', 'http://localhost:8086'),
            token=os.environ.get('INFLUXDB_TOKEN', 'simplex-test-suite-token-change-in-production'),
            org=os.environ.get('INFLUXDB_ORG', 'simplex'),
            bucket=os.environ.get('INFLUXDB_BUCKET', 'metrics'),
        )


class MetricsWriter:
    """
    Writes test metrics to InfluxDB.
    Falls back to logging if InfluxDB is not available.
    """
    
    def __init__(self, config: Optional[MetricsConfig] = None):
        self.config = config or MetricsConfig.from_env()
        self._client: Optional[Any] = None
        self._write_api: Optional[Any] = None
        self._connected = False
        
    def connect(self) -> bool:
        """Establish connection to InfluxDB"""
        if not INFLUXDB_AVAILABLE:
            logger.warning("InfluxDB client not available")
            return False
            
        try:
            self._client = InfluxDBClient(
                url=self.config.url,
                token=self.config.token,
                org=self.config.org
            )
            # Test connection
            self._client.ping()
            self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
            self._connected = True
            logger.info(f"Connected to InfluxDB at {self.config.url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Close InfluxDB connection"""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("Disconnected from InfluxDB")
    
    def write_latency(
        self,
        test_id: str,
        client_id: str,
        latency_ms: float,
        server: str,
        timestamp: Optional[datetime] = None
    ):
        """Write a latency measurement"""
        self._write_point(
            measurement="simplex_test",
            tags={
                "test_id": test_id,
                "client_id": client_id,
                "server": server,
                "metric_type": "latency"
            },
            fields={"latency_ms": float(latency_ms)},
            timestamp=timestamp
        )
    
    def write_message_sent(
        self,
        test_id: str,
        client_id: str,
        server: str,
        message_id: str,
        timestamp: Optional[datetime] = None
    ):
        """Record a sent message"""
        self._write_point(
            measurement="simplex_test",
            tags={
                "test_id": test_id,
                "client_id": client_id,
                "server": server,
                "message_id": message_id
            },
            fields={"messages_sent": 1},
            timestamp=timestamp
        )
    
    def write_message_received(
        self,
        test_id: str,
        client_id: str,
        server: str,
        message_id: str,
        latency_ms: float,
        timestamp: Optional[datetime] = None
    ):
        """Record a received message with latency"""
        self._write_point(
            measurement="simplex_test",
            tags={
                "test_id": test_id,
                "client_id": client_id,
                "server": server,
                "message_id": message_id
            },
            fields={
                "messages_received": 1,
                "latency_ms": float(latency_ms)
            },
            timestamp=timestamp
        )
    
    def write_error(
        self,
        test_id: str,
        client_id: str,
        error_type: str,
        error_message: str,
        server: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """Record an error"""
        tags = {
            "test_id": test_id,
            "client_id": client_id,
            "error_type": error_type
        }
        if server:
            tags["server"] = server
            
        self._write_point(
            measurement="simplex_test",
            tags=tags,
            fields={
                "errors": 1,
                "error_message": error_message
            },
            timestamp=timestamp
        )
    
    def write_test_status(
        self,
        test_id: str,
        status: str,
        active_clients: int,
        messages_sent: int,
        messages_received: int,
        delivery_rate: float,
        avg_latency_ms: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ):
        """Write overall test status"""
        fields = {
            "active_clients": active_clients,
            "messages_sent": messages_sent,
            "messages_received": messages_received,
            "delivery_rate": float(delivery_rate)
        }
        if avg_latency_ms is not None:
            fields["avg_latency_ms"] = float(avg_latency_ms)
            
        self._write_point(
            measurement="simplex_test",
            tags={
                "test_id": test_id,
                "status": status
            },
            fields=fields,
            timestamp=timestamp
        )
    
    def _write_point(
        self,
        measurement: str,
        tags: Dict[str, str],
        fields: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        """Write a single data point to InfluxDB"""
        if not self._connected or not INFLUXDB_AVAILABLE:
            # Fallback to logging
            logger.debug(f"Metric: {measurement} tags={tags} fields={fields}")
            return
        
        try:
            point = Point(measurement)
            for key, value in tags.items():
                point = point.tag(key, value)
            for key, value in fields.items():
                point = point.field(key, value)
            if timestamp:
                point = point.time(timestamp, WritePrecision.MS)
            
            self._write_api.write(bucket=self.config.bucket, record=point)
        except Exception as e:
            logger.error(f"Failed to write metric: {e}")
    
    def write_batch(self, points: List[Dict[str, Any]]):
        """Write multiple points at once"""
        for point_data in points:
            self._write_point(**point_data)


# Global instance for easy access
_metrics_writer: Optional[MetricsWriter] = None


def get_metrics_writer() -> MetricsWriter:
    """Get or create the global metrics writer"""
    global _metrics_writer
    if _metrics_writer is None:
        _metrics_writer = MetricsWriter()
        _metrics_writer.connect()
    return _metrics_writer


def close_metrics_writer():
    """Close the global metrics writer"""
    global _metrics_writer
    if _metrics_writer:
        _metrics_writer.disconnect()
        _metrics_writer = None
