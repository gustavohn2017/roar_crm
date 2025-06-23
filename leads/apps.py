from django.apps import AppConfig


class LeadsConfig(AppConfig):
    name = 'leads'
    verbose_name = 'Gestão de Leads'
    
    def ready(self):
        # Importar sinais se necessário
        # import leads.signals
        pass
