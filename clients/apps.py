from django.apps import AppConfig


class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clients'
    verbose_name = 'SimpleX CLI Clients'
    
    def ready(self):
        # Import signals wenn benötigt
        pass
