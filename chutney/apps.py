"""
Chutney Django App Configuration
"""

from django.apps import AppConfig


class ChutneyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chutney'
    verbose_name = 'Chutney - Private Tor Network'
    
    def ready(self):
        """
        App initialization when Django starts.
        
        Später können wir hier:
        - Signal handlers registrieren
        - Background tasks starten
        - Event listeners initialisieren
        """
        pass