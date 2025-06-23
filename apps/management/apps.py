"""
Apps configuration for the management application.
"""
from django.apps import AppConfig


class ManagementConfig(AppConfig):
    """Management application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.management'
    verbose_name = 'Gestão de Usuários'
    
    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.management.signals
