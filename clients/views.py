"""
Views für SimpleX CLI Clients CRUD

Enthält:
- ClientListView: Übersicht aller Clients
- ClientCreateView: Neuen Client erstellen
- ClientDetailView: Client Details + Aktionen
- ClientUpdateView: Client bearbeiten
- ClientDeleteView: Client löschen
- Action Views: Start, Stop, Connect, SendMessage
"""

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

from .models import SimplexClient, ClientConnection, TestMessage, DeliveryReceipt
from .forms import SimplexClientForm, ClientConnectionForm, TestMessageForm, BatchTestForm
from .services.docker_manager import get_docker_manager

# Später importieren wir hier die Services
# from .services.docker_manager import DockerManager
# from .services.websocket_pool import WebSocketPool


class ClientListView(ListView):
    """
    Übersicht aller SimpleX CLI Clients.
    
    Zeigt Status-Cards mit:
    - Status-Indikator (🟢/⚪/🔴)
    - Port
    - Nachrichtenstatistiken
    - Quick Actions (Start/Stop/Delete)
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
        
        # Statistiken für Header
        context['stats'] = {
            'total': SimplexClient.objects.count(),
            'running': SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING).count(),
            'stopped': SimplexClient.objects.filter(status=SimplexClient.Status.STOPPED).count(),
            'error': SimplexClient.objects.filter(status=SimplexClient.Status.ERROR).count(),
        }
        
        # Freie Ports
        used_ports = set(SimplexClient.objects.values_list('websocket_port', flat=True))
        context['available_ports'] = [p for p in range(3031, 3081) if p not in used_ports][:5]
        
        return context


class ClientCreateView(CreateView):
    """
    Neuen SimpleX Client erstellen.
    
    Erstellt:
    - SimplexClient DB-Eintrag
    - Docker Volume (wird bei Start erstellt)
    """
    model = SimplexClient
    form_class = SimplexClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('clients:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Neuen Client erstellen'
        context['submit_text'] = 'Client erstellen'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Client "{self.object.name}" wurde erstellt.')
        return response


class ClientDetailView(DetailView):
    """
    Detail-Ansicht eines Clients.
    
    Zeigt:
    - Status + Aktionen (Start/Stop/Restart)
    - Container Logs (live)
    - Verbindungen zu anderen Clients
    - Nachrichten-Historie
    - Statistiken
    """
    model = SimplexClient
    template_name = 'clients/detail.html'
    context_object_name = 'client'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object
        
        # Verbindungen (als A oder B)
        context['connections'] = ClientConnection.objects.filter(
            Q(client_a=client) | Q(client_b=client)
        ).select_related('client_a', 'client_b')
        
        # Letzte Nachrichten (gesendet oder empfangen)
        context['recent_messages'] = TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client)
        ).order_by('-created_at')[:20]
        
        # Statistiken
        sent_messages = TestMessage.objects.filter(sender=client)
        context['message_stats'] = {
            'total_sent': sent_messages.count(),
            'delivered': sent_messages.filter(delivery_status=TestMessage.DeliveryStatus.DELIVERED).count(),
            'failed': sent_messages.filter(delivery_status=TestMessage.DeliveryStatus.FAILED).count(),
            'avg_latency': sent_messages.filter(total_latency_ms__isnull=False).aggregate(
                avg=Avg('total_latency_ms')
            )['avg'] or 0,
        }
        
        # Formulare
        context['message_form'] = TestMessageForm(initial={'sender': client})
        context['connection_form'] = ClientConnectionForm(initial={'client_a': client})
        
        # Andere laufende Clients für Quick-Connect
        context['other_running_clients'] = SimplexClient.objects.filter(
            status=SimplexClient.Status.RUNNING
        ).exclude(pk=client.pk)
        
        return context


class ClientUpdateView(UpdateView):
    """
    Client bearbeiten.
    
    Hinweis: Manche Felder (Port, Slug) können nur geändert werden
    wenn der Client gestoppt ist.
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
        context['title'] = f'Client "{self.object.name}" bearbeiten'
        context['submit_text'] = 'Änderungen speichern'
        context['is_edit'] = True
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Client "{self.object.name}" wurde aktualisiert.')
        return response


class ClientDeleteView(DeleteView):
    """
    Client löschen.
    
    Löscht:
    - SimplexClient DB-Eintrag
    - Docker Container (falls vorhanden)
    - Optional: Docker Volume
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
        """Django 4+ nutzt post() statt delete()"""
        client = self.get_object()
        client_name = client.name
        container_name = client.container_name
        
        # Docker Container und Volume löschen ZUERST (bevor DB-Eintrag weg ist)
        remove_volume = request.POST.get('remove_volume') == 'true'
        try:
            docker_manager = get_docker_manager()
            docker_manager.delete_container(client, remove_volume=remove_volume)
            messages.info(request, f'Container "{container_name}" wurde entfernt.')
        except Exception as e:
            messages.warning(request, f'Container konnte nicht gelöscht werden: {e}')
        
        # Jetzt DB-Eintrag löschen
        response = super().post(request, *args, **kwargs)
        messages.success(request, f'Client "{client_name}" wurde gelöscht.')
        return response


# === Action Views (AJAX/POST) ===

class ClientStartView(View):
    """Startet einen Client (Docker Container)"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        
        if client.status == SimplexClient.Status.RUNNING:
            messages.warning(request, f'Client "{client.name}" läuft bereits.')
            return self._redirect(request, client)
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.start_container(client)
            
            messages.success(request, f'Client "{client.name}" wurde gestartet.')
        except Exception as e:
            client.status = SimplexClient.Status.ERROR
            client.last_error = str(e)
            client.save()
            messages.error(request, f'Fehler beim Starten: {e}')
        
        return self._redirect(request, client)
    
    def _redirect(self, request, client):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': client.status,
                'message': 'OK'
            })
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))


class ClientStopView(View):
    """Stoppt einen Client (Docker Container)"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        
        if client.status != SimplexClient.Status.RUNNING:
            messages.warning(request, f'Client "{client.name}" läuft nicht.')
            return self._redirect(request, client)
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.stop_container(client)
            
            messages.success(request, f'Client "{client.name}" wurde gestoppt.')
        except Exception as e:
            client.status = SimplexClient.Status.ERROR
            client.last_error = str(e)
            client.save()
            messages.error(request, f'Fehler beim Stoppen: {e}')
        
        return self._redirect(request, client)
    
    def _redirect(self, request, client):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': client.status,
                'message': 'OK'
            })
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))


class ClientRestartView(View):
    """Startet einen Client neu"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.restart_container(client)
            
            messages.success(request, f'Client "{client.name}" wurde neu gestartet.')
        except Exception as e:
            client.status = SimplexClient.Status.ERROR
            client.last_error = str(e)
            client.save()
            messages.error(request, f'Fehler beim Neustart: {e}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': client.status})
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))


class ClientLogsView(View):
    """Holt Container Logs (AJAX)"""
    
    def get(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        tail = int(request.GET.get('tail', 50))
        
        docker_manager = get_docker_manager()
        logs = docker_manager.get_container_logs(client, tail=tail)
        
        return JsonResponse({
            'logs': logs,
            'status': client.status
        })


# === Connection Views ===

class ConnectionCreateView(View):
    """Erstellt eine Verbindung zwischen zwei Clients"""
    
    def post(self, request):
        form = ClientConnectionForm(request.POST)
        
        if form.is_valid():
            connection = form.save()
            
            # TODO: Verbindung über WebSocket herstellen
            # 1. Einladung von client_a erstellen
            # 2. Einladung bei client_b akzeptieren
            
            messages.success(
                request, 
                f'Verbindung zwischen {connection.client_a.name} und {connection.client_b.name} wird hergestellt...'
            )
            
            # Redirect zum initiierenden Client
            return HttpResponseRedirect(
                reverse('clients:detail', kwargs={'slug': connection.client_a.slug})
            )
        
        messages.error(request, 'Fehler beim Erstellen der Verbindung.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('clients:list')))


class ConnectionDeleteView(View):
    """Löscht eine Verbindung"""
    
    def post(self, request, pk):
        connection = get_object_or_404(ClientConnection, pk=pk)
        client_a_slug = connection.client_a.slug
        
        # TODO: Kontakt auf beiden Seiten löschen via WebSocket
        
        connection.delete()
        messages.success(request, 'Verbindung wurde gelöscht.')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client_a_slug}))


# === Message Testing Views ===

class SendMessageView(View):
    """Sendet eine Test-Nachricht"""
    
    def post(self, request):
        form = TestMessageForm(request.POST)
        
        if form.is_valid():
            sender = form.cleaned_data['sender']
            recipient = form.cleaned_data['recipient']
            content = form.cleaned_data['content']
            
            # Finde die Verbindung
            connection = ClientConnection.objects.filter(
                Q(client_a=sender, client_b=recipient) |
                Q(client_a=recipient, client_b=sender),
                status=ClientConnection.Status.CONNECTED
            ).first()
            
            if not connection:
                messages.error(request, 'Keine aktive Verbindung gefunden.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('clients:list')))
            
            # Erstelle TestMessage
            message = TestMessage.objects.create(
                connection=connection,
                sender=sender,
                recipient=recipient,
                content=content,
                sent_at=timezone.now(),
                delivery_status=TestMessage.DeliveryStatus.SENDING
            )
            
            # TODO: Nachricht via WebSocket senden
            # correlation_id = await websocket_pool.send_message(sender, recipient.profile_name, content)
            # message.correlation_id = correlation_id
            # message.save()
            
            # Temporär: Simuliere erfolgreichen Versand
            message.mark_sent()
            sender.update_stats(sent=1)
            
            messages.success(request, f'Nachricht an {recipient.name} gesendet.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'sent',
                    'message_id': str(message.id)
                })
        else:
            messages.error(request, 'Ungültige Formulardaten.')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('clients:list')))


class MessageStatusView(View):
    """Holt den aktuellen Status einer Nachricht (AJAX Polling)"""
    
    def get(self, request, pk):
        message = get_object_or_404(TestMessage, pk=pk)
        
        return JsonResponse({
            'id': str(message.id),
            'status': message.delivery_status,
            'status_display': message.get_delivery_status_display(),
            'latency_to_server_ms': message.latency_to_server_ms,
            'latency_to_client_ms': message.latency_to_client_ms,
            'total_latency_ms': message.total_latency_ms,
        })


# === Test Panel View ===

class TestPanelView(View):
    """
    Interaktives Test-Panel für Nachrichten-Tests.
    
    Features:
    - Client-zu-Client Auswahl
    - Einzel-Nachrichten
    - Batch-Tests
    - Live-Status Updates
    """
    
    def get(self, request):
        running_clients = SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING)
        connections = ClientConnection.objects.filter(status=ClientConnection.Status.CONNECTED)
        
        # Letzte Test-Nachrichten
        recent_messages = TestMessage.objects.order_by('-created_at')[:50]
        
        context = {
            'running_clients': running_clients,
            'connections': connections,
            'recent_messages': recent_messages,
            'message_form': TestMessageForm(),
            'batch_form': BatchTestForm(),
        }
        
        return render(request, 'clients/test_panel.html', context)


# === Bulk Actions ===

class BulkStartView(View):
    """Startet mehrere Clients gleichzeitig"""
    
    def post(self, request):
        client_ids = request.POST.getlist('client_ids')
        clients = SimplexClient.objects.filter(id__in=client_ids)
        
        docker_manager = get_docker_manager()
        started = 0
        for client in clients:
            if client.status != SimplexClient.Status.RUNNING:
                try:
                    docker_manager.start_container(client)
                    started += 1
                except Exception as e:
                    messages.warning(request, f'Fehler bei {client.name}: {e}')
        
        messages.success(request, f'{started} Clients gestartet.')
        return HttpResponseRedirect(reverse('clients:list'))


class BulkStopView(View):
    """Stoppt mehrere Clients gleichzeitig"""
    
    def post(self, request):
        client_ids = request.POST.getlist('client_ids')
        clients = SimplexClient.objects.filter(id__in=client_ids)
        
        docker_manager = get_docker_manager()
        stopped = 0
        for client in clients:
            if client.status == SimplexClient.Status.RUNNING:
                try:
                    docker_manager.stop_container(client)
                    stopped += 1
                except Exception as e:
                    messages.warning(request, f'Fehler bei {client.name}: {e}')
        
        messages.success(request, f'{stopped} Clients gestoppt.')
        return HttpResponseRedirect(reverse('clients:list'))


# === SimpleX Connection & Messaging Views ===

from .services.simplex_commands import get_simplex_service


class ClientConnectView(View):
    """Verbindet zwei Clients miteinander"""
    
    def post(self, request, slug):
        """
        Verbindet diesen Client mit einem anderen.
        
        POST params:
            target_slug: Slug des Ziel-Clients
        """
        client_a = get_object_or_404(SimplexClient, slug=slug)
        target_slug = request.POST.get('target_slug')
        
        if not target_slug:
            messages.error(request, 'Kein Ziel-Client angegeben.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        client_b = get_object_or_404(SimplexClient, slug=target_slug)
        
        # Prüfe ob beide laufen
        if client_a.status != SimplexClient.Status.RUNNING:
            messages.error(request, f'{client_a.name} läuft nicht.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        if client_b.status != SimplexClient.Status.RUNNING:
            messages.error(request, f'{client_b.name} läuft nicht.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        try:
            svc = get_simplex_service()
            
            # 1. Adresse von Client B holen/erstellen (ZUERST!)
            # Auto-Accept kommt nach Adresse
            
            # 2. Adresse von Client B holen/erstellen
            addr_result = svc.create_or_get_address(client_b)
            if not addr_result.success:
                messages.error(request, f'Konnte keine Adresse erstellen: {addr_result.error}')
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
            
            invitation_link = addr_result.data.get('full_link', '')
            
            # 3. Client A verbindet sich
            connect_result = svc.connect_via_link(client_a, invitation_link)
            if not connect_result.success:
                messages.error(request, f'Verbindung fehlgeschlagen: {connect_result.error}')
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
            
            # 4. ClientConnection in DB erstellen
            connection, created = ClientConnection.objects.get_or_create(
                client_a=client_a,
                client_b=client_b,
                defaults={
                    'invitation_link': invitation_link,
                    'contact_name_on_a': client_b.profile_name,
                    'contact_name_on_b': client_a.profile_name,
                    'status': ClientConnection.Status.CONNECTED,
                    'connected_at': timezone.now(),
                }
            )
            
            if created:
                messages.success(request, f'Verbindung hergestellt: {client_a.name} ↔ {client_b.name}')
            else:
                messages.info(request, f'Verbindung existiert bereits.')
            
        except Exception as e:
            messages.error(request, f'Fehler: {e}')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))


class QuickMessageView(View):
    """Sendet eine schnelle Nachricht an einen verbundenen Client"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        contact_name = request.POST.get('contact_name')
        message_text = request.POST.get('message', 'Test message')
        
        if not contact_name:
            messages.error(request, 'Kein Kontakt angegeben.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        try:
            svc = get_simplex_service()
            result = svc.send_message(client, contact_name, message_text)
            
            if result.success:
                # Finde Verbindung und Empfänger
                connection = ClientConnection.objects.filter(
                    Q(client_a=client, contact_name_on_a=contact_name) |
                    Q(client_b=client, contact_name_on_b=contact_name)
                ).first()
                
                if connection:
                    # Empfänger bestimmen
                    if connection.client_a == client:
                        recipient = connection.client_b
                    else:
                        recipient = connection.client_a
                    
                    # TestMessage erstellen
                    test_msg = TestMessage.objects.create(
                        connection=connection,
                        sender=client,
                        recipient=recipient,
                        content=message_text,
                        sent_at=timezone.now(),
                        delivery_status=TestMessage.DeliveryStatus.SENT,
                    )
                    test_msg.mark_sent()
                    
                    # Stats aktualisieren
                    client.messages_sent += 1
                    recipient.messages_received += 1
                    recipient.save(update_fields=["messages_received"])
                    client.save(update_fields=['messages_sent'])
                
                messages.success(request, f'Nachricht an {contact_name} gesendet.')
            else:
                messages.error(request, f'Senden fehlgeschlagen: {result.error}')
                
        except Exception as e:
            messages.error(request, f'Fehler: {e}')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))


class ClientContactsAPIView(View):
    """API: Listet Kontakte eines Clients (für AJAX)"""
    
    def get(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        
        if client.status != SimplexClient.Status.RUNNING:
            return JsonResponse({'error': 'Client läuft nicht', 'contacts': []})
        
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
            return JsonResponse({'error': str(e), 'contacts': []})
