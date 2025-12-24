from django.shortcuts import render
from servers.models import Server
from stresstests.models import TestRun
from events.models import EventLog

def index(request):
    """Haupt-Dashboard"""
    context = {
        'servers': Server.objects.all()[:10],
        'server_count': Server.objects.count(),
        'active_servers': Server.objects.filter(is_active=True).count(),
        'recent_tests': TestRun.objects.all()[:5],
        'running_tests': TestRun.objects.filter(status='running').count(),
        'recent_events': EventLog.objects.all()[:10],
    }
    return render(request, 'dashboard/index.html', context)

def stats_partial(request):
    """HTMX Partial für Stats-Update"""
    context = {
        'server_count': Server.objects.count(),
        'active_servers': Server.objects.filter(is_active=True).count(),
        'running_tests': TestRun.objects.filter(status='running').count(),
        'total_tests': TestRun.objects.count(),
    }
    return render(request, 'dashboard/_stats.html', context)
