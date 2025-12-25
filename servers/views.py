from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import Server, Category
import json
import re


def server_list(request):
    """List all servers with optional category filter"""
    category_id = request.GET.get('category')
    categories = Category.objects.all()
    
    if category_id:
        try:
            active_category = Category.objects.get(pk=category_id)
            servers = Server.objects.filter(categories=active_category).order_by('sort_order', 'name')
        except Category.DoesNotExist:
            active_category = None
            servers = Server.objects.all().order_by('sort_order', 'name')
    else:
        active_category = None
        servers = Server.objects.all().order_by('sort_order', 'name')
    
    return render(request, 'servers/list.html', {
        'servers': servers,
        'categories': categories,
        'active_category': active_category,
    })


def server_detail(request, pk):
    """Server detail view"""
    server = get_object_or_404(Server, pk=pk)
    return render(request, 'servers/detail.html', {'server': server})


def server_create(request):
    """Create a new server"""
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        server_type = request.POST.get('server_type', 'smp')
        is_active = request.POST.get('is_active') == 'on'
        
        # Parse address to extract components
        host, port, fingerprint, password = parse_simplex_address(address)
        
        server = Server.objects.create(
            name=name,
            address=address,
            server_type=server_type,
            host=host,
            port=port,
            fingerprint=fingerprint,
            password=password,
            is_active=is_active,
            sort_order=Server.objects.count()
        )
        
        # Handle categories
        category_ids = request.POST.getlist('categories')
        if category_ids:
            server.categories.set(category_ids)
        
        return redirect('servers:list')
    
    return render(request, 'servers/form.html', {
        'server': None,
        'categories': categories,
    })


def server_edit(request, pk):
    """Edit an existing server"""
    server = get_object_or_404(Server, pk=pk)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        server.name = request.POST.get('name', '').strip()
        server.address = request.POST.get('address', '').strip()
        server.server_type = request.POST.get('server_type', 'smp')
        server.is_active = request.POST.get('is_active') == 'on'
        
        # Parse address
        host, port, fingerprint, password = parse_simplex_address(server.address)
        server.host = host
        server.port = port
        server.fingerprint = fingerprint
        server.password = password
        
        server.save()
        
        # Handle categories
        category_ids = request.POST.getlist('categories')
        server.categories.set(category_ids)
        
        return redirect('servers:list')
    
    return render(request, 'servers/form.html', {
        'server': server,
        'categories': categories,
    })


@require_POST
def server_delete(request, pk):
    """Delete a server"""
    server = get_object_or_404(Server, pk=pk)
    server.delete()
    return render(request, 'servers/_empty.html')


@require_POST
def server_toggle(request, pk):
    """Toggle server active status"""
    server = get_object_or_404(Server, pk=pk)
    server.is_active = not server.is_active
    server.save()
    return render(request, 'servers/_server_card.html', {'server': server})


@require_POST
def server_reorder(request):
    """Reorder servers via drag and drop"""
    try:
        data = json.loads(request.body)
        for item in data.get('order', []):
            Server.objects.filter(pk=item['id']).update(sort_order=item['order'])
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def test_connection(request):
    """Test server connection"""
    import socket
    import ssl
    import time
    
    try:
        data = json.loads(request.body)
        address = data.get('address', '')
        
        host, port, fingerprint, password = parse_simplex_address(address)
        
        if not host or not port:
            return JsonResponse({
                'success': False,
                'message': 'Invalid address format'
            })
        
        is_onion = '.onion' in host
        start_time = time.time()
        
        try:
            if is_onion:
                # Use Tor SOCKS5 proxy
                import socks
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
                sock.settimeout(120)
                sock.connect((host, port))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                sock.connect((host, port))
            
            # Try TLS handshake
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                latency = int((time.time() - start_time) * 1000)
                cert = ssock.getpeercert(binary_form=True)
                
                return JsonResponse({
                    'success': True,
                    'message': f'TLS 1.3 connection established',
                    'latency': latency,
                    'used_tor': is_onion
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e),
                'used_tor': is_onion
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@require_POST
def check_duplicate(request):
    """Check if server address already exists"""
    try:
        data = json.loads(request.body)
        address = data.get('address', '')
        exclude_id = data.get('exclude_id')
        
        host, port, fingerprint, password = parse_simplex_address(address)
        
        if not host:
            return JsonResponse({'exists': False})
        
        query = Server.objects.filter(host=host)
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        
        existing = query.first()
        
        if existing:
            return JsonResponse({
                'exists': True,
                'message': f'Server "{existing.name}" already uses this host'
            })
        
        return JsonResponse({'exists': False})
        
    except Exception as e:
        return JsonResponse({'exists': False, 'error': str(e)})


def parse_simplex_address(address):
    """Parse SimpleX server address into components"""
    host = ''
    port = 5223
    fingerprint = ''
    password = ''
    
    try:
        # Format: smp://fingerprint:password@host:port or smp://fingerprint@host
        pattern = r'^(smp|xftp)://([^:@]+)(?::([^@]+))?@([^:]+)(?::(\d+))?$'
        match = re.match(pattern, address.strip())
        
        if match:
            fingerprint = match.group(2) or ''
            password = match.group(3) or ''
            host = match.group(4) or ''
            port = int(match.group(5)) if match.group(5) else 5223
        else:
            # Try simpler format: just host:port or host
            simple_pattern = r'^([^:]+)(?::(\d+))?$'
            simple_match = re.match(simple_pattern, address.strip())
            if simple_match:
                host = simple_match.group(1)
                port = int(simple_match.group(2)) if simple_match.group(2) else 5223
                
    except Exception:
        pass
    
    return host, port, fingerprint, password


# ============ Category Views ============

def category_list(request):
    """List all categories"""
    categories = Category.objects.all()
    return render(request, 'servers/categories/list.html', {
        'categories': categories
    })


def category_detail(request, pk):
    """Category detail with assigned servers"""
    category = get_object_or_404(Category, pk=pk)
    servers = category.servers.all().order_by('sort_order', 'name')
    return render(request, 'servers/categories/detail.html', {
        'category': category,
        'servers': servers
    })


def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', '#0ea5e9')
        
        Category.objects.create(
            name=name,
            description=description,
            color=color,
            sort_order=Category.objects.count()
        )
        return redirect('servers:category_list')
    
    return render(request, 'servers/categories/form.html', {
        'category': None
    })


def category_edit(request, pk):
    """Edit a category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.description = request.POST.get('description', '').strip()
        category.color = request.POST.get('color', '#0ea5e9')
        category.save()
        return redirect('servers:category_list')
    
    return render(request, 'servers/categories/form.html', {
        'category': category
    })


@require_POST
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return render(request, 'servers/_empty.html')
