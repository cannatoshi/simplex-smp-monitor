"""
Management Command für Server-Monitoring.
Wird vom Scheduler oder Cron aufgerufen.

Nutzung:
    # Alle aktiven Monitoring-Tests ausführen
    python manage.py run_monitoring

    # Bestimmten Test ausführen
    python manage.py run_monitoring --test-id=1

    # Nur Tests mit bestimmtem Intervall
    python manage.py run_monitoring --interval=5
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from stresstests.models import Test
from stresstests.tasks import run_server_check
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Führt Server-Monitoring-Tests aus'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-id',
            type=int,
            help='Bestimmten Test ausführen (ID)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            help='Nur Tests mit diesem Intervall (Minuten)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Intervall ignorieren und sofort ausführen',
        )

    def handle(self, *args, **options):
        test_id = options.get('test_id')
        interval = options.get('interval')
        force = options.get('force', False)
        
        # Tests filtern
        tests = Test.objects.filter(
            test_type='monitoring',
            status='active'
        )
        
        if test_id:
            tests = tests.filter(pk=test_id)
        
        if interval:
            tests = tests.filter(interval_minutes=interval)
        
        if not tests.exists():
            self.stdout.write(self.style.WARNING('Keine aktiven Monitoring-Tests gefunden'))
            return
        
        now = timezone.now()
        executed = 0
        
        for test in tests:
            # Prüfen ob Zeit für nächsten Check
            if not force and test.last_run:
                next_run = test.last_run + timedelta(minutes=test.interval_minutes)
                if now < next_run:
                    self.stdout.write(
                        f'⏭️  {test.name}: Nächster Run in {(next_run - now).seconds // 60} Min'
                    )
                    continue
            
            self.stdout.write(f'▶️  {test.name}: Starte Check...')
            
            try:
                results = run_server_check(test.pk)
                
                online = sum(1 for r in results if r['success'])
                total = len(results)
                
                self.stdout.write(self.style.SUCCESS(
                    f'   ✓ {online}/{total} Server online'
                ))
                executed += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'   ✗ Fehler: {e}'
                ))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Fertig: {executed} Tests ausgeführt'))
