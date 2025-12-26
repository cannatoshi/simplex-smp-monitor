from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

scheduler = None


def check_and_run_tests():
    """Prüft welche Tests fällig sind und führt sie aus"""
    from .models import Test
    from .tasks import run_server_check
    
    now = timezone.now()
    logger.info(f"🔍 Scheduler Check um {now.strftime('%H:%M:%S')}")
    print(f"🔍 Scheduler Check um {now.strftime('%H:%M:%S')}")
    
    # Hole alle aktiven Monitoring-Tests
    active_tests = Test.objects.filter(
        test_type='monitoring',
        status='active'
    )
    
    for test in active_tests:
        should_run = False
        
        if test.last_run is None:
            # Noch nie gelaufen
            should_run = True
            reason = "erster Run"
        else:
            # Prüfe ob Intervall abgelaufen
            elapsed = (now - test.last_run).total_seconds()
            interval_seconds = test.interval_minutes * 60
            
            if elapsed >= interval_seconds:
                should_run = True
                reason = f"Intervall abgelaufen ({elapsed:.0f}s >= {interval_seconds}s)"
            else:
                reason = f"noch {interval_seconds - elapsed:.0f}s bis zum nächsten Check"
        
        if should_run:
            logger.info(f"▶️ Starte Test '{test.name}' - {reason}")
            print(f"▶️ Starte Test '{test.name}' - {reason}")
            try:
                run_server_check(test.id)
                logger.info(f"✅ Test '{test.name}' abgeschlossen")
                print(f"✅ Test '{test.name}' abgeschlossen")
            except Exception as e:
                logger.error(f"❌ Test '{test.name}' fehlgeschlagen: {e}")
                print(f"❌ Test '{test.name}' fehlgeschlagen: {e}")
        else:
            logger.debug(f"⏭️ Test '{test.name}' - {reason}")


def start_scheduler():
    """Startet den Background-Scheduler"""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler läuft bereits")
        return
    
    scheduler = BackgroundScheduler(timezone='Europe/Berlin')
    
    # Alle 30 Sekunden prüfen (für schnellere Reaktion)
    scheduler.add_job(
        check_and_run_tests,
        trigger=IntervalTrigger(seconds=15),
        id='monitoring_check',
        name='Check Monitoring Tests',
        replace_existing=True,
        max_instances=1
    )
    
    scheduler.start()
    logger.info("🚀 APScheduler gestartet - prüft alle 30 Sekunden")
    print("🚀 APScheduler gestartet - prüft alle 30 Sekunden")


def stop_scheduler():
    """Stoppt den Scheduler"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler gestoppt")
