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
        
        # Gesendete Nachrichten
        context['sent_messages'] = TestMessage.objects.filter(
            sender=client
        ).select_related('recipient').order_by('-created_at')[:20]
        
        # Empfangene Nachrichten
        context['received_messages'] = TestMessage.objects.filter(
            recipient=client
        ).select_related('sender').order_by('-created_at')[:20]
        
        # Alle Nachrichten (für "Alle" Tab)
        all_messages = list(TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client)
        ).select_related('sender', 'recipient').order_by('-created_at')[:30])
        
        # Direction hinzufügen für Template
        for msg in all_messages:
            msg._direction = 'sent' if msg.sender == client else 'received'
        context['all_messages'] = all_messages
        
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
        
        # Container Logs
        try:
            docker_manager = get_docker_manager()
            context['container_logs'] = docker_manager.get_container_logs(client, tail=50)
        except Exception:
            context['container_logs'] = ''
        
        # Formulare
        context['message_form'] = TestMessageForm(initial={'sender': client})
        context['connection_form'] = ClientConnectionForm(initial={'client_a': client})
        
        # Andere laufende Clients für Quick-Connect (ohne bereits verbundene)
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
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if client.status == SimplexClient.Status.RUNNING:
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'{client.name} läuft bereits.'})
            messages.warning(request, f'Client "{client.name}" läuft bereits.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.start_container(client)
            
            # Nutze die neue start() Methode für started_at
            client.start()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'status': client.status,
                    'message': f'{client.name} wurde gestartet.'
                })
            messages.success(request, f'Client "{client.name}" wurde gestartet.')
            
        except Exception as e:
            client.set_error(str(e))
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Fehler beim Starten: {e}')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))


class ClientStopView(View):
    """Stoppt einen Client (Docker Container)"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if client.status != SimplexClient.Status.RUNNING:
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'{client.name} läuft nicht.'})
            messages.warning(request, f'Client "{client.name}" läuft nicht.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.stop_container(client)
            
            # Nutze die neue stop() Methode
            client.stop()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'status': client.status,
                    'message': f'{client.name} wurde gestoppt.'
                })
            messages.success(request, f'Client "{client.name}" wurde gestoppt.')
            
        except Exception as e:
            client.set_error(str(e))
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Fehler beim Stoppen: {e}')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client.slug}))


class ClientRestartView(View):
    """Startet einen Client neu"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            docker_manager = get_docker_manager()
            docker_manager.restart_container(client)
            
            # Nutze start() für neue started_at Zeit
            client.start()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'status': client.status,
                    'message': f'{client.name} wurde neu gestartet.'
                })
            messages.success(request, f'Client "{client.name}" wurde neu gestartet.')
            
        except Exception as e:
            client.set_error(str(e))
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Fehler beim Neustart: {e}')
        
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
                f'Verbindung zwischen {connection.client_a.name} und {connection.client_b.name} wird hergestellt...'
            )
            return HttpResponseRedirect(
                reverse('clients:detail', kwargs={'slug': connection.client_a.slug})
            )
        
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Ungültige Daten.'}, status=400)
        
        messages.error(request, 'Fehler beim Erstellen der Verbindung.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('clients:list')))


class ConnectionDeleteView(View):
    """Löscht eine Verbindung - AJAX Version"""
    
    def post(self, request, pk):
        connection = get_object_or_404(ClientConnection, pk=pk)
        client_a_slug = connection.client_a.slug
        client_a_name = connection.client_a.name
        client_b_name = connection.client_b.name
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        connection.delete()
        
        # WebSocket Event
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
            pass  # Channel layer nicht verfügbar
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Verbindung {client_a_name} ↔ {client_b_name} gelöscht.'
            })
        
        messages.success(request, 'Verbindung wurde gelöscht.')
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': client_a_slug}))


# === Message Testing Views ===

class SendMessageView(View):
    """
    Sendet eine Test-Nachricht - AJAX-kompatibel
    
    Akzeptiert sowohl Form-Daten (TestMessageForm) als auch 
    direkte POST-Parameter vom Template:
    - sender: Client ID
    - contact_name: Name des Kontakts (aus Verbindung)
    - message: Nachrichtentext
    """
    
    def post(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Parameter aus POST holen
        sender_id = request.POST.get('sender')
        contact_name = request.POST.get('contact_name')
        message_text = request.POST.get('message', '').strip()
        
        # Validierung
        if not sender_id:
            error = 'Kein Sender angegeben.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('clients:list')))
        
        if not contact_name:
            error = 'Kein Empfänger angegeben.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('clients:list')))
        
        if not message_text:
            error = 'Keine Nachricht angegeben.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('clients:list')))
        
        try:
            sender = SimplexClient.objects.get(pk=sender_id)
        except SimplexClient.DoesNotExist:
            error = 'Sender nicht gefunden.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=404)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:list'))
        
        # Finde die Verbindung basierend auf contact_name
        connection = ClientConnection.objects.filter(
            Q(client_a=sender, contact_name_on_a=contact_name) |
            Q(client_b=sender, contact_name_on_b=contact_name),
            status=ClientConnection.Status.CONNECTED
        ).first()
        
        if not connection:
            error = f'Keine aktive Verbindung mit "{contact_name}" gefunden.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': sender.slug}))
        
        # Empfänger bestimmen
        if connection.client_a == sender:
            recipient = connection.client_b
        else:
            recipient = connection.client_a
        
        try:
            # SimpleX Service für echtes Senden
            from .services.simplex_commands import get_simplex_service
            svc = get_simplex_service()
            result = svc.send_message(sender, contact_name, message_text)
            
            if not result.success:
                error = f'Senden fehlgeschlagen: {result.error}'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, error)
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': sender.slug}))
            
            # TestMessage in DB erstellen
            test_message = TestMessage.objects.create(
                connection=connection,
                sender=sender,
                recipient=recipient,
                content=message_text,
                sent_at=timezone.now(),
                delivery_status=TestMessage.DeliveryStatus.SENT,
            )
            
            # Stats aktualisieren
            sender.update_stats(sent=1)
            
            # WebSocket Event für Live-Update
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
                            "client_slug": sender.slug,
                            "sender": sender.name,
                            "recipient": recipient.name,
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
                pass  # WebSocket nicht verfügbar
            
            # Erfolg
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message_id': str(test_message.id),
                    'content': message_text,
                    'recipient': recipient.name,
                    'status': 'sent',
                    'messages_sent': sender.messages_sent,
                })
            
            messages.success(request, f'✓ Nachricht an {recipient.name} gesendet.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': sender.slug}))
            
        except Exception as e:
            error = f'Fehler: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=500)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': sender.slug}))


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
                    client.start()  # Nutze neue Methode
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
                    client.stop()  # Nutze neue Methode
                    stopped += 1
                except Exception as e:
                    messages.warning(request, f'Fehler bei {client.name}: {e}')
        
        messages.success(request, f'{stopped} Clients gestoppt.')
        return HttpResponseRedirect(reverse('clients:list'))


# === SimpleX Connection & Messaging Views ===

from .services.simplex_commands import get_simplex_service

class ClientConnectView(View):
    """Verbindet zwei Clients miteinander - AJAX Version"""
    
    def post(self, request, slug):
        client_a = get_object_or_404(SimplexClient, slug=slug)
        target_slug = request.POST.get('target_slug')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not target_slug:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Kein Ziel-Client angegeben.'}, status=400)
            messages.error(request, 'Kein Ziel-Client angegeben.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        client_b = get_object_or_404(SimplexClient, slug=target_slug)
        
        # Prüfe ob beide laufen
        if client_a.status != SimplexClient.Status.RUNNING:
            error = f'{client_a.name} läuft nicht.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        if client_b.status != SimplexClient.Status.RUNNING:
            error = f'{client_b.name} läuft nicht.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, error)
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        try:
            import time
            svc = get_simplex_service()
            
            # 1. Adresse von Client B holen/erstellen
            addr_result = svc.create_or_get_address(client_b)
            if not addr_result.success:
                error = f'Konnte keine Adresse erstellen: {addr_result.error}'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, error)
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
            
            invitation_link = addr_result.data.get('full_link', '')
            
            # 2. Auto-Accept auf Client B aktivieren
            svc.enable_auto_accept(client_b)
            
            # 3. Client A verbindet sich
            connect_result = svc.connect_via_link(client_a, invitation_link)
            if not connect_result.success:
                error = f'Verbindung fehlgeschlagen: {connect_result.error}'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, error)
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
            
            # 4. Warten damit SimpleX die Verbindung aufbauen kann
            time.sleep(3)
            
            # 5. Echte Kontaktnamen aus SimpleX holen
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
            
            # 6. Prüfen ob Kontakte wirklich existieren
            if not contacts_a.success or not contacts_a.data.get('contacts'):
                error = f'Verbindung nicht hergestellt - keine Kontakte auf {client_a.name}'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, error)
                return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
            
            # 7. ClientConnection in DB erstellen/aktualisieren
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
            
            # Auch umgekehrte Connection löschen falls vorhanden
            ClientConnection.objects.filter(client_a=client_b, client_b=client_a).delete()
            
            # WebSocket Event für Live-Update
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
                f'✓ Verbindung hergestellt: {client_a.name} ({contact_name_on_a}) ↔ {client_b.name} ({contact_name_on_b})'
            )
            
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Fehler: {e}')
        
        return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))


class QuickMessageView(View):
    """Sendet eine schnelle Nachricht an einen verbundenen Client - AJAX Version"""
    
    def post(self, request, slug):
        client = get_object_or_404(SimplexClient, slug=slug)
        contact_name = request.POST.get('contact_name')
        message_text = request.POST.get('message', 'Test message')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not contact_name:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Kein Kontakt angegeben.'}, status=400)
            messages.error(request, 'Kein Kontakt angegeben.')
            return HttpResponseRedirect(reverse('clients:detail', kwargs={'slug': slug}))
        
        try:
            svc = get_simplex_service()
            result = svc.send_message(client, contact_name, message_text)
            
            if result.success:
                # Finde Verbindung - Client kann A oder B sein
                connection = ClientConnection.objects.filter(
                    Q(client_a=client, contact_name_on_a=contact_name) |
                    Q(client_b=client, contact_name_on_b=contact_name),
                    status=ClientConnection.Status.CONNECTED
                ).first()
                
                test_msg = None
                recipient = None
                
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
                    
                    # Stats aktualisieren
                    client.update_stats(sent=1)
                    
                    # WebSocket Event
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
                                    "client_slug": client.slug,
                                    "sender": client.name,
                                    "recipient": recipient.name if recipient else contact_name,
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
                        'content': message_text,
                        'recipient': recipient.name if recipient else contact_name,
                        'status': 'sent',
                        'messages_sent': client.messages_sent,
                    })
                
                messages.success(request, f'✓ Nachricht an {contact_name} gesendet.')
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': str(result.error)}, status=400)
                messages.error(request, f'Senden fehlgeschlagen: {result.error}')
                
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
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