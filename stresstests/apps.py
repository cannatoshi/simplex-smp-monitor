from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class StresstestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stresstests'
    
    def ready(self):
        import os
        # Nur im Hauptprozess starten, nicht im Reloader
        if os.environ.get('RUN_MAIN') == 'true':
            try:
                from .scheduler import start_scheduler
                start_scheduler()
                logger.info("✅ APScheduler started successfully")
                print("✅ APScheduler gestartet - Monitoring läuft!")
            except Exception as e:
                logger.error(f"❌ Failed to start scheduler: {e}")
                print(f"❌ Scheduler Fehler: {e}")
