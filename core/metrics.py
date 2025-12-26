from influxdb import InfluxDBClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

_client = None


def get_client():
    """Gibt InfluxDB Client zurück (Singleton)"""
    global _client
    if _client is None:
        try:
            _client = InfluxDBClient(
                host=getattr(settings, 'INFLUXDB_HOST', 'localhost'),
                port=getattr(settings, 'INFLUXDB_PORT', 8086),
                database=getattr(settings, 'INFLUXDB_DATABASE', 'metrics'),
            )
        except Exception as e:
            logger.error(f"Failed to create InfluxDB client: {e}")
    return _client


def write_metric(measurement, tags, fields, timestamp=None):
    """Schreibt eine Metrik nach InfluxDB"""
    client = get_client()
    if not client:
        return False
    
    point = {
        "measurement": measurement,
        "tags": tags,
        "fields": fields,
    }
    
    if timestamp:
        point["time"] = timestamp.isoformat()
    
    try:
        client.write_points([point])
        return True
    except Exception as e:
        logger.error(f"Failed to write metric: {e}")
        return False


class MetricsWriter:
    """Wrapper-Klasse für InfluxDB Metriken"""
    
    def __init__(self):
        self.client = get_client()
    
    def write(self, measurement, tags, fields, timestamp=None):
        return write_metric(measurement, tags, fields, timestamp)
    
    def write_points(self, points):
        if not self.client:
            return False
        try:
            self.client.write_points(points)
            return True
        except Exception as e:
            logger.error(f"Failed to write points: {e}")
            return False


def get_metrics_writer():
    """Factory function für MetricsWriter"""
    return MetricsWriter()
