"""
Clients App Config with Event Bridge Auto-Start
"""

import asyncio
import logging
import threading
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clients'
    
    def ready(self):
        """Startet Event Bridge beim App-Start"""
        import os
        
        # Nur im Hauptprozess starten (nicht in Migrations, etc.)
        if os.environ.get('RUN_MAIN') == 'true':
            self._start_bridge_thread()
    
    def _start_bridge_thread(self):
        """Startet Bridge in separatem Thread mit eigenem Event Loop"""
        def run_bridge():
            from clients.services.event_bridge import start_event_bridge
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                logger.info("🌉 Starting Event Bridge in background thread...")
                loop.run_until_complete(start_event_bridge())
            except Exception as e:
                logger.error(f"Event Bridge error: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_bridge, daemon=True)
        thread.start()
        logger.info("🌉 Event Bridge thread started")
