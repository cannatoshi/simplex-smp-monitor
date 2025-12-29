"""
Dashboard API - Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Min, Max
from django.utils import timezone
from datetime import timedelta

from servers.models import Server
from stresstests.models import Test, TestResult
from events.models import EventLog
from clients.models import SimplexClient
from servers.api.serializers import ServerListSerializer
from stresstests.api.serializers import TestListSerializer
from events.api.serializers import EventLogSerializer
from .serializers import DashboardStatsSerializer


class DashboardStatsView(APIView):
    """
    GET /api/v1/dashboard/stats/ - Dashboard Statistiken
    """
    
    def get(self, request):
        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        
        # Server Stats
        servers = Server.objects.all()
        total_servers = servers.count()
        active_servers = servers.filter(is_active=True).count()
        online_servers = servers.filter(last_status='online').count()
        offline_servers = servers.filter(last_status='offline').count()
        smp_servers = servers.filter(server_type='smp').count()
        xftp_servers = servers.filter(server_type='xftp').count()
        onion_servers = servers.filter(address__contains='.onion').count()
        
        # Test Stats
        tests = Test.objects.all()
        total_tests = tests.count()
        active_tests = tests.filter(status='active').count()
        running_tests = tests.filter(status='running').count()
        
        # Client Stats
        clients = SimplexClient.objects.all()
        total_clients = clients.count()
        running_clients = clients.filter(status='running').count()
        
        # Event Stats
        events = EventLog.objects.all()
        total_events = events.count()
        error_events_24h = events.filter(
            level__in=['ERROR', 'CRITICAL'],
            created_at__gte=day_ago
        ).count()
        
        # Aggregated Stats
        avg_latency = servers.filter(
            last_latency__isnull=False
        ).aggregate(avg=Avg('last_latency'))['avg']
        
        # Overall uptime
        servers_with_checks = servers.filter(total_checks__gt=0)
        if servers_with_checks.exists():
            total_checks = sum(s.total_checks for s in servers_with_checks)
            successful_checks = sum(s.successful_checks for s in servers_with_checks)
            overall_uptime = (successful_checks / total_checks * 100) if total_checks > 0 else None
        else:
            overall_uptime = None
        
        data = {
            'total_servers': total_servers,
            'active_servers': active_servers,
            'online_servers': online_servers,
            'offline_servers': offline_servers,
            'smp_servers': smp_servers,
            'xftp_servers': xftp_servers,
            'onion_servers': onion_servers,
            'total_tests': total_tests,
            'active_tests': active_tests,
            'running_tests': running_tests,
            'total_clients': total_clients,
            'running_clients': running_clients,
            'total_events': total_events,
            'error_events_24h': error_events_24h,
            'avg_latency': round(avg_latency, 2) if avg_latency else None,
            'overall_uptime': round(overall_uptime, 2) if overall_uptime else None,
        }
        
        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)


class ServerActivityView(APIView):
    """
    GET /api/v1/dashboard/activity/ - Server-Aktivität (24h)
    """
    
    def get(self, request):
        hours = int(request.query_params.get('hours', 24))
        now = timezone.now()
        
        activity = []
        for i in range(hours, 0, -1):
            hour_start = now - timedelta(hours=i)
            hour_end = now - timedelta(hours=i-1)
            
            results = TestResult.objects.filter(
                timestamp__gte=hour_start,
                timestamp__lt=hour_end
            )
            
            checks = results.count()
            online = results.filter(success=True).count()
            offline = results.filter(success=False).count()
            avg_latency = results.filter(
                latency_ms__isnull=False
            ).aggregate(avg=Avg('latency_ms'))['avg']
            
            activity.append({
                'hour': hour_start.isoformat(),
                'checks': checks,
                'online': online,
                'offline': offline,
                'avg_latency': round(avg_latency, 2) if avg_latency else None
            })
        
        return Response(activity)


class LatencyOverviewView(APIView):
    """
    GET /api/v1/dashboard/latency/ - Latenz-Übersicht pro Server
    """
    
    def get(self, request):
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        servers = Server.objects.filter(
            is_active=True,
            last_latency__isnull=False
        ).order_by('name')
        
        latency_data = []
        for server in servers:
            results = TestResult.objects.filter(
                server=server,
                timestamp__gte=since,
                latency_ms__isnull=False
            )
            
            stats = results.aggregate(
                avg=Avg('latency_ms'),
                min=Min('latency_ms'),
                max=Max('latency_ms')
            )
            
            latency_data.append({
                'server_id': server.id,
                'server_name': server.name,
                'avg_latency': round(stats['avg'], 2) if stats['avg'] else None,
                'min_latency': stats['min'],
                'max_latency': stats['max'],
                'last_latency': server.last_latency
            })
        
        return Response(latency_data)


class RecentServersView(APIView):
    """
    GET /api/v1/dashboard/servers/ - Letzte Server-Status
    """
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        servers = Server.objects.filter(
            is_active=True
        ).order_by('-last_check')[:limit]
        
        serializer = ServerListSerializer(servers, many=True)
        return Response(serializer.data)


class RecentTestsView(APIView):
    """
    GET /api/v1/dashboard/tests/ - Letzte Tests
    """
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        tests = Test.objects.order_by('-last_run')[:limit]
        
        serializer = TestListSerializer(tests, many=True)
        return Response(serializer.data)


class RecentEventsView(APIView):
    """
    GET /api/v1/dashboard/events/ - Letzte Events
    """
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        level = request.query_params.get('level')
        
        events = EventLog.objects.all()
        if level:
            events = events.filter(level=level.upper())
        
        events = events.order_by('-created_at')[:limit]
        
        serializer = EventLogSerializer(events, many=True)
        return Response(serializer.data)
