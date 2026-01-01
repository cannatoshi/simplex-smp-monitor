import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Server, Category
import json, re, socket, ssl, time

logger = logging.getLogger(__name__)


def parse_simplex_address(address):
    try:
        match = re.match(r'^(smp|xftp)://([^:@]+)(?::([^@]+))?@([^:]+)(?::(\d+))?$', address.strip())
        if match:
            return match.group(4), int(match.group(5) or 5223), match.group(2), match.group(3) or ''
    except: pass
    return '', 5223, '', ''

def server_list(request):
    category_id = request.GET.get('category')
    categories = Category.objects.all()
    if category_id:
        try:
            active_category = Category.objects.get(pk=category_id)
            servers = Server.objects.filter(categories=active_category).order_by('name')
        except Category.DoesNotExist:
            active_category = None
            servers = Server.objects.all().order_by('name')
    else:
        active_category = None
        servers = Server.objects.all().order_by('name')
    return render(request, 'servers/list.html', {
        'servers': servers,
        'categories': categories,
        'active_category': active_category,
    })

def server_detail(request, pk):
    return render(request, 'servers/detail.html', {'server': get_object_or_404(Server, pk=pk)})

def server_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        server = Server.objects.create(
            name=request.POST.get('name', '').strip(),
            address=request.POST.get('address', '').strip(),
            server_type=request.POST.get('server_type', 'smp'),
            is_active=request.POST.get('is_active') == 'on',
        )
        category_ids = request.POST.getlist('categories')
        if category_ids:
            server.categories.set(category_ids)
        if request.POST.get('test_status') == 'online':
            server.last_status = 'online'
            server.last_check = timezone.now()
            server.save()
        return redirect('servers:list')
    return render(request, 'servers/form.html', {'server': None, 'categories': categories})

def server_edit(request, pk):
    server = get_object_or_404(Server, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        server.name = request.POST.get('name', '').strip()
        server.address = request.POST.get('address', '').strip()
        server.server_type = request.POST.get('server_type', 'smp')
        server.is_active = request.POST.get('is_active') == 'on'
        if request.POST.get('test_status') == 'online':
            server.last_status = 'online'
            server.last_check = timezone.now()
        server.save()
        category_ids = request.POST.getlist('categories')
        server.categories.set(category_ids)
        return redirect('servers:list')
    return render(request, 'servers/form.html', {'server': server, 'categories': categories})

@require_POST
def server_delete(request, pk):
    get_object_or_404(Server, pk=pk).delete()
    return render(request, 'servers/_empty.html')

@require_POST
def server_toggle(request, pk):
    server = get_object_or_404(Server, pk=pk)
    server.is_active = not server.is_active
    server.save()
    return render(request, 'servers/_server_card.html', {'server': server})

@require_POST
def server_reorder(request):
    return JsonResponse({'success': True})

@require_POST
def test_connection(request):
    try:
        data = json.loads(request.body)
        host, port, _, _ = parse_simplex_address(data.get('address', ''))
        if not host: return JsonResponse({'success': False, 'message': 'Invalid address'})
        is_onion = '.onion' in host
        start = time.time()
        if is_onion:
            import socks
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            sock.settimeout(120)
        else:
            sock = socket.socket()
            sock.settimeout(30)
        sock.connect((host, port))
        ctx = ssl.create_default_context()
        # SECURITY NOTE: Hostname/cert verification disabled intentionally.
        # SimpleX servers use self-signed certificates.
        # This is required for .onion and self-hosted server testing.
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(sock, server_hostname=host):
            return JsonResponse({'success': True, 'message': 'TLS OK', 'latency': int((time.time()-start)*1000), 'used_tor': is_onion})
    except Exception as e:
        logger.exception('Connection test failed')
        return JsonResponse({'success': False, 'message': 'Connection failed'})

@require_POST
def test_server(request, pk):
    server = get_object_or_404(Server, pk=pk)
    host, port, _, _ = parse_simplex_address(server.address)
    try:
        if '.onion' in host:
            import socks
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            sock.settimeout(120)
        else:
            sock = socket.socket()
            sock.settimeout(30)
        sock.connect((host, port))
        ctx = ssl.create_default_context()
        # SECURITY NOTE: Hostname/cert verification disabled intentionally.
        # SimpleX servers use self-signed certificates.
        # This is required for .onion and self-hosted server testing.
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(sock, server_hostname=host):
            server.last_status = 'online'
    except:
        server.last_status = 'error'
    server.last_check = timezone.now()
    server.save()
    return render(request, 'servers/_server_card.html', {'server': server})

@require_POST
def check_duplicate(request):
    try:
        data = json.loads(request.body)
        host, _, _, _ = parse_simplex_address(data.get('address', ''))
        if not host: return JsonResponse({'exists': False})
        exclude = data.get('exclude_id')
        for srv in Server.objects.all():
            if exclude and srv.pk == int(exclude): continue
            if parse_simplex_address(srv.address)[0] == host:
                return JsonResponse({'exists': True, 'message': f'"{srv.name}" uses this host'})
        return JsonResponse({'exists': False})
    except:
        return JsonResponse({'exists': False})

# ============ Category Views ============
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'servers/categories/list.html', {'categories': categories})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    servers = category.servers.all().order_by('name')
    return render(request, 'servers/categories/detail.html', {'category': category, 'servers': servers})

def category_create(request):
    if request.method == 'POST':
        Category.objects.create(
            name=request.POST.get('name', '').strip(),
            description=request.POST.get('description', '').strip(),
            color=request.POST.get('color', '#0ea5e9'),
        )
        return redirect('servers:category_list')
    return render(request, 'servers/categories/form.html', {'category': None})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.description = request.POST.get('description', '').strip()
        category.color = request.POST.get('color', '#0ea5e9')
        category.save()
        return redirect('servers:category_list')
    return render(request, 'servers/categories/form.html', {'category': category})

@require_POST
def category_delete(request, pk):
    get_object_or_404(Category, pk=pk).delete()
    return render(request, 'servers/_empty.html')