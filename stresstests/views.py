from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import TestRun, Metric
from servers.models import Server

def test_list(request):
    tests = TestRun.objects.all()[:20]
    return render(request, 'stresstests/list.html', {'tests': tests})

def test_detail(request, pk):
    test = get_object_or_404(TestRun, pk=pk)
    metrics = test.metrics.all()[:100]
    return render(request, 'stresstests/detail.html', {'test': test, 'metrics': metrics})

@require_http_methods(["GET", "POST"])
def test_create(request):
    if request.method == 'POST':
        test = TestRun.objects.create(
            name=request.POST.get('name', f'Test {timezone.now().strftime("%Y-%m-%d %H:%M")}'),
            num_clients=int(request.POST.get('num_clients', 2)),
            duration_seconds=int(request.POST.get('duration_seconds', 60)),
            message_interval_seconds=int(request.POST.get('message_interval_seconds', 5)),
        )
        # Server hinzufügen
        server_ids = request.POST.getlist('servers')
        if server_ids:
            test.servers.set(server_ids)
        return redirect('stresstests:detail', pk=test.pk)
    
    servers = Server.objects.filter(is_active=True)
    return render(request, 'stresstests/create.html', {'servers': servers})

@require_http_methods(["POST"])
def test_start(request, pk):
    test = get_object_or_404(TestRun, pk=pk)
    test.status = 'running'
    test.started_at = timezone.now()
    test.save()
    # TODO: Hier würde der eigentliche Test gestartet werden
    if request.htmx:
        return render(request, 'stresstests/_test_status.html', {'test': test})
    return redirect('stresstests:detail', pk=pk)

@require_http_methods(["POST"])
def test_stop(request, pk):
    test = get_object_or_404(TestRun, pk=pk)
    test.status = 'cancelled'
    test.finished_at = timezone.now()
    test.save()
    if request.htmx:
        return render(request, 'stresstests/_test_status.html', {'test': test})
    return redirect('stresstests:detail', pk=pk)

def test_metrics_api(request, pk):
    """API Endpoint für Echtzeit-Metriken"""
    test = get_object_or_404(TestRun, pk=pk)
    metrics = list(test.metrics.values('timestamp', 'metric_type', 'value')[:50])
    return JsonResponse({
        'test_id': test.pk,
        'status': test.status,
        'messages_sent': test.messages_sent,
        'messages_received': test.messages_received,
        'delivery_rate': test.delivery_rate,
        'metrics': metrics
    })
