from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.db.models import Max
from django.utils import timezone
import json
import socket
import time
import re
from .models import Server, Category

TOR_PROXY_HOST = '127.0.0.1'
TOR_PROXY_PORT = 9050


# =============================================================================
# SERVER VIEWS
# =============================================================================

def server_list(request):
    servers = Server.objects.all()
    if request.htmx:
        return render(request, 'servers/_server_list.html', {'servers': servers})
    return render(request, 'servers/list.html', {'servers': servers})


def server_detail(request, pk):
    server = get_object_or_404(Server, pk=pk)
    return render(request, 'servers/detail.html', {'server': server})


@require_http_methods(["GET", "POST"])
def server_create(request):
    categories = Category.objects.all()
    
    if request.method == 'POST':
        max_order = Server.objects.aggregate(Max('sort_order'))['sort_order__max'] or 0
        test_status = request.POST.get('test_status', '')
        
        server = Server.objects.create(
            name=request.POST.get('name'),
            server_type=request.POST.get('server_type', 'smp'),
            address=request.POST.get('address'),
            is_active=request.POST.get('is_active') == 'on',
            sort_order=max_order + 1,
            last_status=test_status if test_status else 'unknown',
            last_check=timezone.now() if test_status else None
        )
        
        # Handle categories
        category_ids = request.POST.getlist('categories')
        if category_ids:
            server.categories.set(category_ids)
        
        return redirect('servers:list')
    
    return render(request, 'servers/form.html', {'server': None, 'categories': categories})


@require_http_methods(["GET", "POST"])
def server_edit(request, pk):
    server = get_object_or_404(Server, pk=pk)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        server.name = request.POST.get('name')
        server.server_type = request.POST.get('server_type', 'smp')
        server.address = request.POST.get('address')
        server.is_active = request.POST.get('is_active') == 'on'
        
        test_status = request.POST.get('test_status', '')
        if test_status:
            server.last_status = test_status
            server.last_check = timezone.now()
        
        server.save()
        
        # Handle categories
        category_ids = request.POST.getlist('categories')
        server.categories.set(category_ids)
        
        return redirect('servers:list')
    
    return render(request, 'servers/form.html', {'server': server, 'categories': categories})


@require_http_methods(["POST"])
def server_toggle(request, pk):
    server = get_object_or_404(Server, pk=pk)
    server.is_active = not server.is_active
    server.save()
    if request.htmx:
        return render(request, 'servers/_server_card.html', {'server': server})
    return redirect('servers:list')


@require_http_methods(["POST"])
def server_delete(request, pk):
    server = get_object_or_404(Server, pk=pk)
    server.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('servers:list')


@require_http_methods(["POST"])
def server_reorder(request):
    try:
        data = json.loads(request.body)
        order_list = data.get('order', [])
        for item in order_list:
            Server.objects.filter(pk=item['id']).update(sort_order=item['order'])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_http_methods(["POST"])
def check_duplicate(request):
    try:
        data = json.loads(request.body)
        address = data.get('address', '').strip()
        exclude_id = data.get('exclude_id')
        
        if not address:
            return JsonResponse({'exists': False})
        
        queryset = Server.objects.filter(address=address)
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        
        exists = queryset.exists()
        
        if exists:
            server = queryset.first()
            return JsonResponse({
                'exists': True,
                'server_name': server.name,
                'message': f'This address is already used by "{server.name}"'
            })
        
        return JsonResponse({'exists': False})
        
    except Exception as e:
        return JsonResponse({'exists': False, 'error': str(e)})


@require_http_methods(["POST"])
def test_connection(request):
    try:
        data = json.loads(request.body)
        address = data.get('address', '').strip()
        
        if not address:
            return JsonResponse({'success': False, 'message': 'No address provided'})
        
        pattern = r'^(smp|xftp)://[^@]+@([^:]+):?(\d+)?$'
        match = re.match(pattern, address)
        
        if not match:
            pattern_simple = r'^(smp|xftp)://[^@]+@(.+)$'
            match = re.match(pattern_simple, address)
        
        if not match:
            return JsonResponse({
                'success': False,
                'message': 'Invalid address format. Expected: smp://fingerprint@host or smp://fingerprint:password@host'
            })
        
        protocol = match.group(1)
        host = match.group(2)
        
        if match.lastindex >= 3 and match.group(3):
            port = int(match.group(3))
        else:
            port = 5223 if protocol == 'smp' else 443
        
        is_onion = '.onion' in host
        used_tor = False
        
        start_time = time.time()
        
        try:
            if is_onion:
                used_tor = True
                success, message = test_via_tor(host, port)
            else:
                success, message = test_direct(host, port)
            
            latency = round((time.time() - start_time) * 1000)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Server reachable at {host}:{port}',
                    'latency': latency,
                    'used_tor': used_tor
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': message,
                    'used_tor': used_tor
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e),
                'used_tor': is_onion
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


def test_direct(host, port, timeout=10):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, 'Connection successful'
        else:
            return False, f'Connection refused (error code: {result})'
    except socket.timeout:
        return False, 'Connection timeout'
    except socket.gaierror:
        return False, 'DNS resolution failed'
    except Exception as e:
        return False, str(e)


def test_via_tor(host, port, timeout=30):
    try:
        import socks
    except ImportError:
        return False, 'PySocks not installed. Run: pip install pysocks'
    
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, TOR_PROXY_HOST, TOR_PROXY_PORT)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True, 'Connection successful via Tor'
    except socks.ProxyConnectionError:
        return False, f'Cannot connect to Tor proxy at {TOR_PROXY_HOST}:{TOR_PROXY_PORT}. Is Tor running?'
    except socks.SOCKS5Error as e:
        return False, f'SOCKS5 error: {e}'
    except socket.timeout:
        return False, 'Connection timeout (Tor can be slow, try again)'
    except Exception as e:
        return False, str(e)


# =============================================================================
# CATEGORY VIEWS
# =============================================================================

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'servers/categories/list.html', {'categories': categories})


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    servers = category.servers.all()
    return render(request, 'servers/categories/detail.html', {'category': category, 'servers': servers})


@require_http_methods(["GET", "POST"])
def category_create(request):
    if request.method == 'POST':
        max_order = Category.objects.aggregate(Max('sort_order'))['sort_order__max'] or 0
        Category.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            color=request.POST.get('color', '#0ea5e9'),
            sort_order=max_order + 1
        )
        return redirect('servers:category_list')
    return render(request, 'servers/categories/form.html', {'category': None})


@require_http_methods(["GET", "POST"])
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.color = request.POST.get('color', '#0ea5e9')
        category.save()
        return redirect('servers:category_list')
    return render(request, 'servers/categories/form.html', {'category': category})


@require_http_methods(["POST"])
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('servers:category_list')
