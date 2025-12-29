"""
Dashboard API - Serializers
"""
from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard Statistiken"""
    total_servers = serializers.IntegerField()
    active_servers = serializers.IntegerField()
    online_servers = serializers.IntegerField()
    offline_servers = serializers.IntegerField()
    smp_servers = serializers.IntegerField()
    xftp_servers = serializers.IntegerField()
    onion_servers = serializers.IntegerField()
    
    total_tests = serializers.IntegerField()
    active_tests = serializers.IntegerField()
    running_tests = serializers.IntegerField()
    
    total_clients = serializers.IntegerField()
    running_clients = serializers.IntegerField()
    
    total_events = serializers.IntegerField()
    error_events_24h = serializers.IntegerField()
    
    avg_latency = serializers.FloatField(allow_null=True)
    overall_uptime = serializers.FloatField(allow_null=True)
