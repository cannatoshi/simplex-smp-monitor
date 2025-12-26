from django.db.models import Avg, Min, Max
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone
from .models import Test, TestResult, Metric
from servers.models import Server
import json


def test_list(request):
    """Liste aller Tests (alle Typen)"""
    test_type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')
    
    tests = Test.objects.all()
    
    if test_type_filter:
        tests = tests.filter(test_type=test_type_filter)
    if status_filter:
        tests = tests.filter(status=status_filter)
    
    # Statistiken
    stats = {
        'total': Test.objects.count(),
        'active': Test.objects.filter(status__in=['active', 'running']).count(),
        'monitoring': Test.objects.filter(test_type='monitoring').count(),
        'stress': Test.objects.filter(test_type='stress').count(),
    }
    
    return render(request, 'stresstests/list.html', {
        'tests': tests[:50],
        'stats': stats,
        'test_type_filter': test_type_filter,
        'status_filter': status_filter,
    })


def test_type_select(request):
    """Auswahl des Test-Typs vor dem Erstellen"""
    return render(request, 'stresstests/type_select.html')


@require_http_methods(["GET", "POST"])
def test_create(request, test_type='monitoring'):
    """Test erstellen - je nach Typ unterschiedliches Formular"""
    
    if test_type not in ['monitoring', 'stress', 'latency']:
        test_type = 'monitoring'
    
    servers = Server.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Basis-Felder
        test = Test.objects.create(
            name=request.POST.get('name', f'{test_type.title()} Test {timezone.now():%Y-%m-%d %H:%M}'),
            description=request.POST.get('description', ''),
            test_type=test_type,
            test_all_active_servers=request.POST.get('test_all_servers') == 'on',
            write_to_influxdb=request.POST.get('write_to_influxdb', 'on') == 'on',
        )
        
        # Server hinzufügen (wenn nicht "alle")
        if not test.test_all_active_servers:
            server_ids = request.POST.getlist('servers')
            if server_ids:
                test.servers.set(server_ids)
        
        # Typ-spezifische Felder
        if test_type == 'monitoring':
            test.interval_minutes = int(request.POST.get('interval_minutes', 5))
            test.save()
        elif test_type == 'stress':
            test.num_clients = int(request.POST.get('num_clients', 2))
            test.duration_seconds = int(request.POST.get('duration_seconds', 60))
            test.message_interval_seconds = int(request.POST.get('message_interval_seconds', 5))
            test.save()
        
        return redirect('stresstests:detail', pk=test.pk)
    
    template = f'stresstests/create_{test_type}.html'
    return render(request, template, {
        'servers': servers,
        'test_type': test_type,
    })




def get_server_stats_summary(test):
    """Berechnet Server-Statistiken für Kachel-Anzeige"""
    servers = test.target_servers
    
    onion_count = sum(1 for s in servers if s.is_onion)
    clear_count = sum(1 for s in servers if not s.is_onion)
    smp_count = sum(1 for s in servers if s.server_type == 'smp')
    xftp_count = sum(1 for s in servers if s.server_type == 'xftp')
    
    return {
        'onion_count': onion_count,
        'clear_count': clear_count,
        'smp_count': smp_count,
        'xftp_count': xftp_count,
        'total_servers': servers.count() if hasattr(servers, 'count') else len(list(servers)),
    }

def get_latency_history(test):
    """Berechnet Latenz-History für Sparkline Chart"""
    from .models import TestResult
    results = TestResult.objects.filter(
        test=test,
        success=True,
        latency_ms__isnull=False
    ).order_by('-timestamp')[:48]
    
    if not results:
        return []
    
    latencies = [r.latency_ms for r in reversed(results)]
    max_lat = max(latencies) if latencies else 1
    
    history = []
    for lat in latencies:
        height = max(10, int((lat / max_lat) * 100))
        history.append({'value': lat, 'height': height})
    
    return history

def test_detail(request, pk):
    """Test-Detail-Ansicht"""
    test = get_object_or_404(Test, pk=pk)
    
    # Letzte Ergebnisse
    recent_results = test.results.select_related('server')[:100]
    
    # Server-Statistiken
    server_stats = []
    for server in test.target_servers:
        results = test.results.filter(server=server)
        total = results.count()
        success = results.filter(success=True).count()
        
        # Letzte Latenz
        last_result = results.first()
        
        server_stats.append({
            'server': server,
            'total_checks': total,
            'success_rate': round((success / total * 100), 1) if total > 0 else None,
            'last_status': 'online' if (last_result and last_result.success) else 'offline' if last_result else 'unknown',
            'last_latency': last_result.latency_ms if last_result else None,
            'last_check': last_result.timestamp if last_result else None,
        })
    
    # Template je nach Typ
    template = f'stresstests/detail_{test.test_type}.html'
    
    # Fallback auf generisches Template
    try:
        return render(request, template, {
            'test': test,
            'recent_results': recent_results,
        'avg_latency': TestResult.objects.filter(test=test, success=True, latency_ms__isnull=False).aggregate(avg=Avg('latency_ms'))['avg'],
        'min_latency': TestResult.objects.filter(test=test, success=True, latency_ms__isnull=False).aggregate(min=Min('latency_ms'))['min'],
        'max_latency': TestResult.objects.filter(test=test, success=True, latency_ms__isnull=False).aggregate(max=Max('latency_ms'))['max'],
        'latency_history': get_latency_history(test),
        'server_summary': get_server_stats_summary(test),
            'server_stats': server_stats,
        })
    except:
        return render(request, 'stresstests/detail.html', {
            'test': test,
            'recent_results': recent_results,
        'avg_latency': TestResult.objects.filter(test=test, success=True, latency_ms__isnull=False).aggregate(avg=Avg('latency_ms'))['avg'],
        'min_latency': TestResult.objects.filter(test=test, success=True, latency_ms__isnull=False).aggregate(min=Min('latency_ms'))['min'],
        'max_latency': TestResult.objects.filter(test=test, success=True, latency_ms__isnull=False).aggregate(max=Max('latency_ms'))['max'],
        'latency_history': get_latency_history(test),
        'server_summary': get_server_stats_summary(test),
            'server_stats': server_stats,
        })


@require_http_methods(["GET", "POST"])
def test_edit(request, pk):
    """Test bearbeiten"""
    test = get_object_or_404(Test, pk=pk)
    servers = Server.objects.filter(is_active=True)
    
    if request.method == 'POST':
        test.name = request.POST.get('name', test.name)
        test.description = request.POST.get('description', '')
        test.test_all_active_servers = request.POST.get('test_all_servers') == 'on'
        test.write_to_influxdb = request.POST.get('write_to_influxdb', 'on') == 'on'
        
        if not test.test_all_active_servers:
            server_ids = request.POST.getlist('servers')
            test.servers.set(server_ids)
        
        # Typ-spezifische Felder
        if test.test_type == 'monitoring':
            test.interval_minutes = int(request.POST.get('interval_minutes', 5))
        elif test.test_type == 'stress':
            test.num_clients = int(request.POST.get('num_clients', 2))
            test.duration_seconds = int(request.POST.get('duration_seconds', 60))
            test.message_interval_seconds = int(request.POST.get('message_interval_seconds', 5))
        
        test.save()
        return redirect('stresstests:detail', pk=test.pk)
    
    template = f'stresstests/edit_{test.test_type}.html'
    try:
        return render(request, template, {'test': test, 'servers': servers})
    except:
        return render(request, 'stresstests/edit.html', {'test': test, 'servers': servers})


@require_POST
def test_delete(request, pk):
    """Test löschen"""
    test = get_object_or_404(Test, pk=pk)
    test.delete()
    
    if request.htmx:
        return render(request, 'stresstests/_empty.html')
    return redirect('stresstests:list')


@require_POST
def test_toggle(request, pk):
    """Test aktivieren/deaktivieren"""
    test = get_object_or_404(Test, pk=pk)
    
    if test.is_active:
        test.deactivate()
    else:
        test.activate()
    
    if request.htmx:
        return render(request, 'stresstests/_test_card.html', {'test': test})
    return redirect('stresstests:detail', pk=pk)


@require_POST
def test_run_now(request, pk):
    """Test sofort einmal ausführen"""
    test = get_object_or_404(Test, pk=pk)
    
    # Import hier um circular imports zu vermeiden
    from .tasks import run_server_check
    
    results = run_server_check(test.pk)
    
    if request.htmx:
        return render(request, 'stresstests/_test_results.html', {
            'test': test,
            'results': results,
        })
    return redirect('stresstests:detail', pk=pk)


def test_metrics_api(request, pk):
    """API Endpoint für Echtzeit-Metriken"""
    test = get_object_or_404(Test, pk=pk)
    
    # Letzte Ergebnisse
    results = list(test.results.values(
        'timestamp', 'server__name', 'success', 'latency_ms', 'error_message'
    )[:50])
    
    # Server-Status
    server_status = {}
    for server in test.target_servers:
        last = test.results.filter(server=server).first()
        server_status[server.name] = {
            'online': last.success if last else None,
            'latency': last.latency_ms if last else None,
            'last_check': last.timestamp.isoformat() if last else None,
        }
    
    return JsonResponse({
        'test_id': test.pk,
        'status': test.status,
        'total_runs': test.total_runs,
        'success_rate': test.success_rate,
        'last_run': test.last_run.isoformat() if test.last_run else None,
        'server_status': server_status,
        'recent_results': results,
    })


# ============ Legacy Views für Abwärtskompatibilität ============

def test_start(request, pk):
    """Legacy: Test starten"""
    return test_toggle(request, pk)


def test_stop(request, pk):
    """Legacy: Test stoppen"""
    return test_toggle(request, pk)
