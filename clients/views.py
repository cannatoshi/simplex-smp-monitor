"""
SimpleX SMP Monitor by cannatoshi
GitHub: https://github.com/cannatoshi/simplex-smp-monitor
Licensed under AGPL-3.0

Views for SimpleX CLI Clients CRUD

Contains:
- ClientListView: Overview of all clients
- ClientCreateView: Create new client
- ClientDetailView: Client details + actions
- ClientUpdateView: Edit client
- ClientDeleteView: Delete client
- Action Views: Start, Stop, Connect, SendMessage
"""
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Q
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
from .models import SimplexClient, ClientConnection, TestMessage, DeliveryReceipt
from .forms import SimplexClientForm, ClientConnectionForm, TestMessageForm, BatchTestForm
from .services.docker_manager import get_docker_manager

logger = logging.getLogger(__name__)


# =============================================================================
# LIST / CRUD VIEWS
# =============================================================================

class ClientListView(ListView):
    """
    Overview of all SimpleX CLI clients.
    
    Shows status cards with:
    - Status indicator (🟢/⚪/🔴)
    - Port
    - Message statistics
    - Quick actions (Start/Stop/Delete)
    """
    model = SimplexClient
    template_name = 'clients/list.html'
    context_object_name = 'clients'
    
    def get_queryset(self):
        return SimplexClient.objects.annotate(
            connection_count=Count('connections_as_a') + Count('connections_as_b')
        ).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics for header
        context['stats'] = {
            'total': SimplexClient.objects.count(),
            'running': SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING).count(),
            'stopped': SimplexClient.objects.filter(status=SimplexClient.Status.STOPPED).count(),
            'error': SimplexClient.objects.filter(status=SimplexClient.Status.ERROR).count(),
        }
        
        # Available ports
        used_ports = set(SimplexClient.objects.values_list('websocket_port', flat=True))
        context['available_ports'] = [p for p in range(3031, 3081) if p not in used_ports][:5]
        
        return context


class ClientCreateView(CreateView):
    """
    Create a new SimpleX client.
    
    Creates:
    - SimplexClient DB entry
    - Docker volume (created on start)
    """
    model = SimplexClient
    form_class = SimplexClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('clients:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Client'
        context['submit_text'] = 'Create Client'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Client "{self.object.name}" was created.')
        return response


class ClientDetailView(DetailView):
    """
    Detail view of a client.
    
    Shows:
    - Status + actions (Start/Stop/Restart)
    - Container logs (live)
    - Connections to other clients
    - Message history
    - Statistics
    """
    model = SimplexClient
    template_name = 'clients/detail.html'
    context_object_name = 'client'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object
        
        # Connections (as A or B)
        context['connections'] = ClientConnection.objects.filter(
            Q(client_a=client) | Q(client_b=client)
        ).select_related('client_a', 'client_b')
        
        # Sent messages
        context['sent_messages'] = TestMessage.objects.filter(
            sender=client
        ).select_related('recipient').order_by('-created_at')[:20]
        
        # Received messages
        context['received_messages'] = TestMessage.objects.filter(
            recipient=client
        ).select_related('sender').order_by('-created_at')[:20]
        
        # All messages (for "All" tab)
        all_messages = list(TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client)
        ).select_related('sender', 'recipient').order_by('-created_at')[:30])
        
        # Add direction for template
        for msg in all_messages:
            msg._direction = 'sent' if msg.sender == client else 'received'
        context['all_messages'] = all_messages
        
        # Statistics
        sent_messages = TestMessage.objects.filter(sender=client)
        context['message_stats'] = {
            'total_sent': sent_messages.count(),
            'delivered': sent_messages.filter(delivery_status=TestMessage.DeliveryStatus.DELIVERED).count(),
            'failed': sent_messages.filter(delivery_status=TestMessage.DeliveryStatus.FAILED).count(),
            'avg_latency': sent_messages.filter(total_latency_ms__isnull=False).aggregate(
                avg=Avg('total_latency_ms')
            )['avg'] or 0,
        }
        
        # Container logs
        try:
            docker_manager = get_docker_manager()
            context['container_logs'] = docker_manager.get_container_logs(client, tail=50)
        except Exception:
            context['container_logs'] = ''
        
        # Forms
        context['message_form'] = TestMessageForm(initial={'sender': client})
        context['connection_form'] = ClientConnectionForm(initial={'client_a': client})
        
        # Other running clients for quick connect (excluding already connected)
        connected_client_ids = set()
        for conn in context['connections']:
            connected_client_ids.add(conn.client_a_id)
            connected_client_ids.add(conn.client_b_id)
        
        context['other_running_clients'] = SimplexClient.objects.filter(
            status=SimplexClient.Status.RUNNING
        ).exclude(
            pk=client.pk
        ).exclude(
            pk__in=connected_client_ids
        )
        
        return context


class ClientUpdateView(UpdateView):
    """
    Edit client.
    
    Note: Some fields (port, slug) can only be changed
    when the client is stopped.
    """
    model = SimplexClient
    form_class = SimplexClientForm
    template_name = 'clients/form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_success_url(self):
        return reverse('clients:detail', kwargs={'slug': self.object.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Client "{self.object.name}"'
        context['submit_text'] = 'Save Changes'
        context['is_edit'] = True
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Client "{self.object.name}" was updated.')
        return response


class ClientDeleteView(DeleteView):
    """
    Delete client.
    
    Deletes:
    - SimplexClient DB entry
    - Docker container (if exists)
    - Optional: Docker volume
    """
    model = SimplexClient
    template_name = 'clients/confirm_delete.html'
    success_url = reverse_lazy('clients:list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['remove_volume'] = self.request.GET.get('remove_volume', 'false') == 'true'
        return context
    
    def post(self, request, *args, **kwargs):
        """Django 4+ uses post() instead of delete()"""
        client = self.get_object()
        client_name = client.name
        container_name = client.container_name
        
        # Delete Docker container and volume FIRST (before DB entry is gone)
        remove_volume = request.POST.get('remove_volume') == 'true'
        try:
            docker_manager = get_docker_manager()
            docker_manager.delete_container(client, remove_volume=remove_volume)
            messages.info(request, f'Container "{container_name}" was removed.')
        except Exception as e:
            logger.exception(f'Failed to delete container {container_name}')
            messages.warning(request, f'Container could not be deleted.')
        
        # Now delete DB entry
        response = super().post(request, *args, **kwargs)
        messages.success(request, f'Client "{client_name}" was deleted.')
        return response


# =============================================================================
# ACTION VIEWS (AJAX/POST)
# =============================================================================

class ClientStartView(View):
    """Start a client (Docker container)"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if client.status == SimplexClient.Status.RUNNING:
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'{client.name} is already running.'})
            messages.warning(request, f'Client "{client.name}" is already running.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.start_container(client)
            
            # Use the start() method for started_at timestamp
            client.start()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'status': client.status,
                    'message': f'{client.name} was started.'
                })
            messages.success(request, f'Client "{client.name}" was started.')
            
        except Exception as e:
            logger.exception(f'Failed to start client {client.name}')
            client.set_error(str(e))
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Failed to start client'}, status=500)
            messages.error(request, 'Error starting client.')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))


class ClientStopView(View):
    """Stop a client (Docker container)"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if client.status != SimplexClient.Status.RUNNING:
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'{client.name} is not running.'})
            messages.warning(request, f'Client "{client.name}" is not running.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.stop_container(client)
            
            # Use the stop() method
            client.stop()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'status': client.status,
                    'message': f'{client.name} was stopped.'
                })
            messages.success(request, f'Client "{client.name}" was stopped.')
            
        except Exception as e:
            logger.exception(f'Failed to stop client {client.name}')
            client.set_error(str(e))
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Failed to stop client'}, status=500)
            messages.error(request, 'Error stopping client.')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))


class ClientRestartView(View):
    """Restart a client"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.restart_container(client)
            
            # Use start() for new started_at timestamp
            client.start()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'status': client.status,
                    'message': f'{client.name} was restarted.'
                })
            messages.success(request, f'Client "{client.name}" was restarted.')
            
        except Exception as e:
            logger.exception(f'Failed to restart client {client.name}')
            client.set_error(str(e))
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Failed to restart client'}, status=500)
            messages.error(request, 'Error restarting client.')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))


class ClientLogsView(View):
    """Get container logs (AJAX)"""
    
    def get(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        tail = int(request.GET.get('tail', 50))
            
        try:
            docker_manager = get_docker_manager()
            logs = docker_manager.get_container_logs(client, tail=tail) or ''
            return JsonResponse({'logs': logs[:50000], 'status': client.status})
        except Exception:
            logger.exception(f'Failed to get logs for {client.name}')
            return JsonResponse({'logs': '[Error fetching logs]', 'status': client.status})


# =============================================================================
# CONNECTION VIEWS
# =============================================================================

class ConnectionCreateView(View):
    """Create a connection between two clients"""
    
    def post(self, request):
        form = ClientConnectionForm(request.POST)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form.is_valid():
            connection = form.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'connection_id': str(connection.pk),
                    'client_a': connection.client_a.name,
                    'client_b': connection.client_b.name,
                })
            
            messages.success(
                request, 
                f'Connection between {connection.client_a.name} and {connection.client_b.name} is being established...'
            )
            return HttpResponseRedirect(
                reverse('clients:detail', kwargs={'slug': connection.client_a.slug})
            )
        
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Invalid data.'}, status=400)
        
        messages.error(request, 'Error creating connection.')
        return HttpResponseRedirect(reverse('clients:list'))


@method_decorator(csrf_exempt, name="dispatch")
class ConnectionDeleteView(View):
    """Delete a connection - AJAX version"""
    
    def post(self, request, pk):
        connection = get_object_or_404(ClientConnection, pk=pk)
        client_a_slug = connection.client_a.slug
        client_a_name = connection.client_a.name
        client_b_name = connection.client_b.name
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        connection.delete()
        
        # WebSocket event
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "clients_all",
                    {
                        "type": "connection_deleted",
                        "connection_id": str(pk),
                        "client_a_slug": client_a_slug,
                    }
                )
        except Exception:
            pass  # Channel layer not available
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Connection {client_a_name} ↔ {client_b_name} deleted.'
            })
        
        messages.success(request, 'Connection was deleted.')
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client_a_slug}))


# =============================================================================
# MESSAGE TESTING VIEWS
# =============================================================================

@method_decorator(csrf_exempt, name="dispatch")
class SendMessageView(View):
    """
    Send a test message - AJAX compatible
    
    Accepts both form data (TestMessageForm) and 
    direct POST parameters from template:
    - sender: Client ID
    - contact_name: Contact name (from connection)
    - message: Message text
    
    IMPORTANT: Uses tracking_id for reliable delivery tracking.
    The Event Bridge will match delivery receipts using this ID.
    """
    
    def post(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Get parameters from POST
        sender_id = request.POST.get('sender')
        contact_name = request.POST.get('contact_name')
        message_text = request.POST.get('message', '').strip()
        
        # Validation
        if not sender_id:
            error = 'No sender specified.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:list'))
        
        if not contact_name:
            error = 'No recipient specified.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:list'))
        
        if not message_text:
            error = 'No message specified.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:list'))
        
        try:
            sender = SimplexClient.objects.get(pk=sender_id)
        except SimplexClient.DoesNotExist:
            error = 'Sender not found.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=404)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:list'))
        
        # Find connection based on contact_name
        connection = ClientConnection.objects.filter(
            Q(client_a=sender, contact_name_on_a=contact_name) |
            Q(client_b=sender, contact_name_on_b=contact_name),
            status=ClientConnection.Status.CONNECTED
        ).first()
        
        if not connection:
            error = f'No active connection with "{contact_name}" found.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': sender.slug}))
        
        # Determine recipient
        if connection.client_a == sender:
            recipient = connection.client_b
        else:
            recipient = connection.client_a
        
        try:
            # Create TestMessage FIRST to get the tracking_id
            # The tracking_id is auto-generated in model.save()
            test_message = TestMessage.objects.create(
                connection=connection,
                sender=sender,
                recipient=recipient,
                content=message_text,
                sent_at=timezone.now(),
                delivery_status=TestMessage.DeliveryStatus.SENDING,
            )
            
            # Send via SimpleX with tracking_id embedded in message
            from .services.simplex_commands import get_simplex_service
            svc = get_simplex_service()
            result = svc.send_message(
                sender, 
                contact_name, 
                message_text, 
                tracking_id=test_message.tracking_id
            )
            
            if not result.success:
                # Mark message as failed
                test_message.mark_failed(result.error or 'Send failed')
                error = 'Send failed'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, error)
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': sender.slug}))
            
            # Update message status to SENT
            test_message.delivery_status = TestMessage.DeliveryStatus.SENT
            test_message.save(update_fields=['delivery_status'])
            
            # Update sender stats only - recipient stats handled by Event Bridge!
            sender.update_stats(sent=1)
            
            # WebSocket event for live update
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        "clients_all",
                        {
                            "type": "new_message",
                            "message_id": str(test_message.id),
                            "tracking_id": test_message.tracking_id,
                            "client_slug": sender.slug,
                            "sender": sender.name,
                            "sender_profile": sender.profile_name,
                            "recipient": recipient.name,
                            "recipient_profile": recipient.profile_name,
                            "content": message_text[:50],
                            "status": "sent",
                            "timestamp": timezone.now().isoformat(),
                        }
                    )
                    async_to_sync(channel_layer.group_send)(
                        "clients_all",
                        {
                            "type": "client_stats",
                            "client_slug": sender.slug,
                            "messages_sent": sender.messages_sent,
                            "messages_received": sender.messages_received,
                        }
                    )
            except Exception:
                pass  # WebSocket not available
            
            # Success
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message_id': str(test_message.id),
                    'tracking_id': test_message.tracking_id,
                    'content': message_text,
                    'recipient': recipient.name,
                    'recipient_profile': recipient.profile_name,
                    'status': 'sent',
                    'messages_sent': sender.messages_sent,
                })
            
            messages.success(request, f'✓ Message sent to {recipient.name}.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': sender.slug}))
            
        except Exception as e:
            logger.exception(f'Failed to send message from {sender.name}')
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Failed to send message'}, status=500)
            messages.error(request, 'Error sending message.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': sender.slug}))


class MessageStatusView(View):
    """Get current status of a message (AJAX polling)"""
    
    def get(self, request, pk):
        message = get_object_or_404(TestMessage, pk=pk)
        
        return JsonResponse({
            'id': str(message.id),
            'tracking_id': message.tracking_id,
            'status': message.delivery_status,
            'status_display': message.get_delivery_status_display(),
            'latency_to_server_ms': message.latency_to_server_ms,
            'latency_to_client_ms': message.latency_to_client_ms,
            'total_latency_ms': message.total_latency_ms,
        })


# =============================================================================
# TEST PANEL VIEW
# =============================================================================

class TestPanelView(View):
    """
    Interactive test panel for message tests.
    
    Features:
    - Client-to-client selection
    - Single messages
    - Batch tests
    - Live status updates
    """
    
    def get(self, request):
        running_clients = SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING)
        connections = ClientConnection.objects.filter(status=ClientConnection.Status.CONNECTED)
        
        # Recent test messages
        recent_messages = TestMessage.objects.order_by('-created_at')[:50]
        
        context = {
            'running_clients': running_clients,
            'connections': connections,
            'recent_messages': recent_messages,
            'message_form': TestMessageForm(),
            'batch_form': BatchTestForm(),
        }
        
        return render(request, 'clients/test_panel.html', context)


# =============================================================================
# BULK ACTIONS
# =============================================================================

class BulkStartView(View):
    """Start multiple clients at once"""
    
    def post(self, request):
        client_ids = request.POST.getlist('client_ids')
        clients = SimplexClient.objects.filter(id__in=client_ids)
        
        docker_manager = get_docker_manager()
        started = 0
        for client in clients:
            if client.status != SimplexClient.Status.RUNNING:
                try:
                    docker_manager.start_container(client)
                    client.start()
                    started += 1
                except Exception as e:
                    logger.exception(f'Failed to start client {client.name}')
                    messages.warning(request, f'Error with {client.name}')
        
        messages.success(request, f'{started} clients started.')
        return HttpResponseRedirect(reverse('clients:list'))


class BulkStopView(View):
    """Stop multiple clients at once"""
    
    def post(self, request):
        client_ids = request.POST.getlist('client_ids')
        clients = SimplexClient.objects.filter(id__in=client_ids)
        
        docker_manager = get_docker_manager()
        stopped = 0
        for client in clients:
            if client.status == SimplexClient.Status.RUNNING:
                try:
                    docker_manager.stop_container(client)
                    client.stop()
                    stopped += 1
                except Exception as e:
                    logger.exception(f'Failed to stop client {client.name}')
                    messages.warning(request, f'Error with {client.name}')
        
        messages.success(request, f'{stopped} clients stopped.')
        return HttpResponseRedirect(reverse('clients:list'))


# =============================================================================
# SIMPLEX CONNECTION & MESSAGING VIEWS
# =============================================================================

from .services.simplex_commands import get_simplex_service


@method_decorator(csrf_exempt, name="dispatch")
class ClientConnectView(View):
    """Connect two clients - AJAX version"""
    
    def post(self, request, slug):
        client_a = get_object_or_404(SimplexClient, slug=slug)
        target_slug = request.POST.get('target_slug')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not target_slug:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'No target client specified.'}, status=400)
            messages.error(request, 'No target client specified.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        client_b = get_object_or_404(SimplexClient, slug=target_slug)
        
        # Check if both are running
        if client_a.status != SimplexClient.Status.RUNNING:
            error = f'{client_a.name} is not running.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        if client_b.status != SimplexClient.Status.RUNNING:
            error = f'{client_b.name} is not running.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        try:
            import time
            svc = get_simplex_service()
            
            # 1. Get/create address from Client B
            addr_result = svc.create_or_get_address(client_b)
            if not addr_result.success:
                error = 'Could not create address'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, error)
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
            
            invitation_link = addr_result.data.get('full_link', '')
            
            # 2. Enable auto-accept on Client B
            svc.enable_auto_accept(client_b)
            
            # 3. Client A connects
            connect_result = svc.connect_via_link(client_a, invitation_link)
            if not connect_result.success:
                error = 'Connection failed'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, error)
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
            
            # 4. Wait for SimpleX to establish connection
            time.sleep(3)
            
            # 5. Get actual contact names from SimpleX
            contact_name_on_a = None
            contact_name_on_b = None
            
            contacts_a = svc.get_contacts(client_a)
            if contacts_a.success:
                for c in contacts_a.data.get('contacts', []):
                    display_name = c.get('localDisplayName', '')
                    if client_b.profile_name in display_name:
                        contact_name_on_a = display_name
                        break
            
            contacts_b = svc.get_contacts(client_b)
            if contacts_b.success:
                for c in contacts_b.data.get('contacts', []):
                    display_name = c.get('localDisplayName', '')
                    if client_a.profile_name in display_name:
                        contact_name_on_b = display_name
                        break
            
            if not contact_name_on_a:
                contact_name_on_a = client_b.profile_name
            if not contact_name_on_b:
                contact_name_on_b = client_a.profile_name
            
            # 6. Check if contacts actually exist
            if not contacts_a.success or not contacts_a.data.get('contacts'):
                error = f'Connection not established - no contacts on {client_a.name}'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, error)
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
            
            # 7. Create/update ClientConnection in DB
            connection, created = ClientConnection.objects.update_or_create(
                client_a=client_a,
                client_b=client_b,
                defaults={
                    'invitation_link': invitation_link,
                    'contact_name_on_a': contact_name_on_a,
                    'contact_name_on_b': contact_name_on_b,
                    'status': ClientConnection.Status.CONNECTED,
                    'connected_at': timezone.now(),
                }
            )
            
            # Delete reverse connection if exists
            ClientConnection.objects.filter(client_a=client_b, client_b=client_a).delete()
            
            # WebSocket event for live update
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        "clients_all",
                        {
                            "type": "connection_created",
                            "connection_id": str(connection.pk),
                            "client_a_slug": client_a.slug,
                            "client_b_slug": client_b.slug,
                            "client_a_name": client_a.name,
                            "client_b_name": client_b.name,
                            "contact_name_on_a": contact_name_on_a,
                            "contact_name_on_b": contact_name_on_b,
                            "status": "connected",
                        }
                    )
            except Exception:
                pass
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'connection_id': str(connection.pk),
                    'client_a': client_a.name,
                    'client_b': client_b.name,
                    'contact_name_on_a': contact_name_on_a,
                    'contact_name_on_b': contact_name_on_b,
                })
            
            messages.success(
                request, 
                f'✓ Connection established: {client_a.name} ({contact_name_on_a}) ↔ {client_b.name} ({contact_name_on_b})'
            )
            
        except Exception as e:
            logger.exception(f'Failed to connect {client_a.name} to {client_b.name}')
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Connection failed'}, status=500)
            messages.error(request, 'Error connecting.')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))


class QuickMessageView(View):
    """
    Send a quick message to a connected client - AJAX version
    
    IMPORTANT: Uses tracking_id for reliable delivery tracking.
    The Event Bridge matches delivery receipts using this ID.
    """
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        contact_name = request.POST.get('contact_name')
        message_text = request.POST.get('message', 'Test message')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not contact_name:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'No contact specified.'}, status=400)
            messages.error(request, 'No contact specified.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        try:
            # Find connection - Client can be A or B
            connection = ClientConnection.objects.filter(
                Q(client_a=client, contact_name_on_a=contact_name) |
                Q(client_b=client, contact_name_on_b=contact_name),
                status=ClientConnection.Status.CONNECTED
            ).first()
            
            test_msg = None
            recipient = None
            
            if connection:
                # Determine recipient
                if connection.client_a == client:
                    recipient = connection.client_b
                else:
                    recipient = connection.client_a
                
                # Create TestMessage FIRST to get tracking_id
                test_msg = TestMessage.objects.create(
                    connection=connection,
                    sender=client,
                    recipient=recipient,
                    content=message_text,
                    sent_at=timezone.now(),
                    delivery_status=TestMessage.DeliveryStatus.SENDING,
                )
            
            # Send via SimpleX with tracking_id
            svc = get_simplex_service()
            result = svc.send_message(
                client, 
                contact_name, 
                message_text,
                tracking_id=test_msg.tracking_id if test_msg else None
            )
            
            if result.success:
                if test_msg:
                    # Update status to SENT
                    test_msg.delivery_status = TestMessage.DeliveryStatus.SENT
                    test_msg.save(update_fields=['delivery_status'])
                    
                    # Update sender stats only - Event Bridge handles recipient!
                    client.update_stats(sent=1)
                    
                    # WebSocket event
                    try:
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        channel_layer = get_channel_layer()
                        if channel_layer:
                            async_to_sync(channel_layer.group_send)(
                                "clients_all",
                                {
                                    "type": "new_message",
                                    "message_id": str(test_msg.id),
                                    "tracking_id": test_msg.tracking_id,
                                    "client_slug": client.slug,
                                    "sender": client.name,
                                    "sender_profile": client.profile_name,
                                    "recipient": recipient.name if recipient else contact_name,
                                    "recipient_profile": recipient.profile_name if recipient else '',
                                    "content": message_text,
                                    "status": "sent",
                                    "timestamp": timezone.now().isoformat(),
                                }
                            )
                            async_to_sync(channel_layer.group_send)(
                                "clients_all",
                                {
                                    "type": "client_stats",
                                    "client_slug": client.slug,
                                    "messages_sent": client.messages_sent,
                                    "messages_received": client.messages_received,
                                }
                            )
                    except Exception:
                        pass
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message_id': str(test_msg.id) if test_msg else None,
                        'tracking_id': test_msg.tracking_id if test_msg else None,
                        'content': message_text,
                        'recipient': recipient.name if recipient else contact_name,
                        'recipient_profile': recipient.profile_name if recipient else '',
                        'status': 'sent',
                        'messages_sent': client.messages_sent,
                    })
                
                messages.success(request, f'✓ Message sent to {contact_name}.')
            else:
                # Mark as failed if we created a test message
                if test_msg:
                    test_msg.mark_failed(result.error or 'Send failed')
                
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Send failed'}, status=400)
                messages.error(request, 'Send failed')
                
        except Exception as e:
            logger.exception(f'Failed to send quick message from {client.name}')
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Failed to send message'}, status=500)
            messages.error(request, 'Error sending.')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))


class ClientContactsAPIView(View):
    """API: List contacts of a client (for AJAX)"""
    
    def get(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        
        if client.status != SimplexClient.Status.RUNNING:
            return JsonResponse({'error': 'Client is not running', 'contacts': []})
        
        try:
            svc = get_simplex_service()
            result = svc.get_contacts(client)
            
            contacts = []
            for c in result.data.get('contacts', []):
                contacts.append({
                    'name': c.get('localDisplayName', 'unknown'),
                    'status': c.get('activeConn', {}).get('connStatus', 'unknown'),
                })
            
            return JsonResponse({'contacts': contacts})
            
        except Exception as e:
            logger.exception(f'Failed to get contacts for {client.name}')
            return JsonResponse({'error': 'Failed to get contacts', 'contacts': []})