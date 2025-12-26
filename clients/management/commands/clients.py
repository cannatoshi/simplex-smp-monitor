"""
Django Management Command für SimpleX CLI Clients

Ermöglicht Verwaltung der Clients über die Kommandozeile:
    python manage.py clients list
    python manage.py clients start <slug>
    python manage.py clients stop <slug>
    python manage.py clients logs <slug>
    python manage.py clients sync
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from clients.models import SimplexClient, ClientConnection
from clients.services.docker_manager import get_docker_manager


class Command(BaseCommand):
    help = 'Verwaltet SimpleX CLI Clients'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Aktion')
        
        # List
        list_parser = subparsers.add_parser('list', help='Listet alle Clients')
        list_parser.add_argument('--running', action='store_true', help='Nur laufende')
        
        # Start
        start_parser = subparsers.add_parser('start', help='Startet einen Client')
        start_parser.add_argument('slug', help='Client Slug')
        
        # Stop
        stop_parser = subparsers.add_parser('stop', help='Stoppt einen Client')
        stop_parser.add_argument('slug', help='Client Slug')
        
        # Restart
        restart_parser = subparsers.add_parser('restart', help='Startet Client neu')
        restart_parser.add_argument('slug', help='Client Slug')
        
        # Logs
        logs_parser = subparsers.add_parser('logs', help='Zeigt Container Logs')
        logs_parser.add_argument('slug', help='Client Slug')
        logs_parser.add_argument('--tail', type=int, default=50, help='Anzahl Zeilen')
        
        # Sync
        subparsers.add_parser('sync', help='Synchronisiert Status mit Docker')
        
        # Start All
        subparsers.add_parser('start-all', help='Startet alle Clients')
        
        # Stop All
        subparsers.add_parser('stop-all', help='Stoppt alle Clients')
        
        # Cleanup
        subparsers.add_parser('cleanup', help='Entfernt verwaiste Container')

    def handle(self, *args, **options):
        action = options.get('action')
        
        if not action:
            self.print_help('manage.py', 'clients')
            return
        
        if action == 'list':
            self.handle_list(options)
        elif action == 'start':
            self.handle_start(options['slug'])
        elif action == 'stop':
            self.handle_stop(options['slug'])
        elif action == 'restart':
            self.handle_restart(options['slug'])
        elif action == 'logs':
            self.handle_logs(options['slug'], options['tail'])
        elif action == 'sync':
            self.handle_sync()
        elif action == 'start-all':
            self.handle_start_all()
        elif action == 'stop-all':
            self.handle_stop_all()
        elif action == 'cleanup':
            self.handle_cleanup()

    def handle_list(self, options):
        """Listet alle Clients"""
        queryset = SimplexClient.objects.all()
        
        if options.get('running'):
            queryset = queryset.filter(status=SimplexClient.Status.RUNNING)
        
        if not queryset.exists():
            self.stdout.write(self.style.WARNING('Keine Clients gefunden'))
            return
        
        self.stdout.write(f"\n{'Slug':<20} {'Name':<25} {'Status':<12} {'Port':<8} {'Sent':<8}")
        self.stdout.write("-" * 80)
        
        for client in queryset:
            status_style = {
                'running': self.style.SUCCESS,
                'stopped': lambda x: x,
                'error': self.style.ERROR,
            }.get(client.status, lambda x: x)
            
            self.stdout.write(
                f"{client.slug:<20} "
                f"{client.name:<25} "
                f"{status_style(client.status.ljust(12))} "
                f"{str(client.websocket_port):<8} "
                f"{str(client.messages_sent):<8}"
            )
        
        self.stdout.write("")

    def handle_start(self, slug: str):
        """Startet einen Client"""
        client = self._get_client(slug)
        
        self.stdout.write(f"Starte {client.name}...")
        
        try:
            dm = get_docker_manager()
            if dm.start_container(client):
                self.stdout.write(self.style.SUCCESS(f"✓ {client.name} gestartet"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ Start fehlgeschlagen: {client.last_error}"))
        except Exception as e:
            raise CommandError(f"Fehler: {e}")

    def handle_stop(self, slug: str):
        """Stoppt einen Client"""
        client = self._get_client(slug)
        
        self.stdout.write(f"Stoppe {client.name}...")
        
        try:
            dm = get_docker_manager()
            if dm.stop_container(client):
                self.stdout.write(self.style.SUCCESS(f"✓ {client.name} gestoppt"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ Stop fehlgeschlagen: {client.last_error}"))
        except Exception as e:
            raise CommandError(f"Fehler: {e}")

    def handle_restart(self, slug: str):
        """Startet einen Client neu"""
        client = self._get_client(slug)
        
        self.stdout.write(f"Restarte {client.name}...")
        
        try:
            dm = get_docker_manager()
            if dm.restart_container(client):
                self.stdout.write(self.style.SUCCESS(f"✓ {client.name} neugestartet"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ Restart fehlgeschlagen"))
        except Exception as e:
            raise CommandError(f"Fehler: {e}")

    def handle_logs(self, slug: str, tail: int):
        """Zeigt Container Logs"""
        client = self._get_client(slug)
        
        self.stdout.write(f"\n=== Logs: {client.name} (tail={tail}) ===\n")
        
        try:
            dm = get_docker_manager()
            logs = dm.get_container_logs(client, tail=tail)
            self.stdout.write(logs)
        except Exception as e:
            raise CommandError(f"Fehler: {e}")

    def handle_sync(self):
        """Synchronisiert Status aller Clients mit Docker"""
        self.stdout.write("Synchronisiere Client-Status mit Docker...")
        
        try:
            dm = get_docker_manager()
            updated = 0
            
            for client in SimplexClient.objects.all():
                old_status = client.status
                dm.sync_status(client)
                if client.status != old_status:
                    self.stdout.write(f"  {client.slug}: {old_status} → {client.status}")
                    updated += 1
            
            self.stdout.write(self.style.SUCCESS(f"✓ {updated} Clients aktualisiert"))
        except Exception as e:
            raise CommandError(f"Fehler: {e}")

    def handle_start_all(self):
        """Startet alle Clients"""
        clients = SimplexClient.objects.exclude(status=SimplexClient.Status.RUNNING)
        
        if not clients.exists():
            self.stdout.write("Alle Clients laufen bereits")
            return
        
        self.stdout.write(f"Starte {clients.count()} Clients...")
        
        dm = get_docker_manager()
        started = 0
        
        for client in clients:
            try:
                if dm.start_container(client):
                    self.stdout.write(self.style.SUCCESS(f"  ✓ {client.name}"))
                    started += 1
                else:
                    self.stdout.write(self.style.ERROR(f"  ✗ {client.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ {client.name}: {e}"))
        
        self.stdout.write(f"\n{started}/{clients.count()} Clients gestartet")

    def handle_stop_all(self):
        """Stoppt alle laufenden Clients"""
        clients = SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING)
        
        if not clients.exists():
            self.stdout.write("Keine laufenden Clients")
            return
        
        self.stdout.write(f"Stoppe {clients.count()} Clients...")
        
        dm = get_docker_manager()
        stopped = 0
        
        for client in clients:
            try:
                if dm.stop_container(client):
                    self.stdout.write(self.style.SUCCESS(f"  ✓ {client.name}"))
                    stopped += 1
                else:
                    self.stdout.write(self.style.ERROR(f"  ✗ {client.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ {client.name}: {e}"))
        
        self.stdout.write(f"\n{stopped}/{clients.count()} Clients gestoppt")

    def handle_cleanup(self):
        """Entfernt verwaiste Docker Container"""
        self.stdout.write("Suche verwaiste Container...")
        
        try:
            dm = get_docker_manager()
            removed = dm.cleanup_orphaned_containers()
            self.stdout.write(self.style.SUCCESS(f"✓ {removed} Container entfernt"))
        except Exception as e:
            raise CommandError(f"Fehler: {e}")

    def _get_client(self, slug: str) -> SimplexClient:
        """Holt Client oder wirft Fehler"""
        try:
            return SimplexClient.objects.get(slug=slug)
        except SimplexClient.DoesNotExist:
            raise CommandError(f"Client '{slug}' nicht gefunden")
