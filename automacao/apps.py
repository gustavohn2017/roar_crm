from django.apps import AppConfig

class AutomacaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'automacao'
    verbose_name = 'Automação de Marketing e Vendas'
    
    def ready(self):
        # Importar signals quando a app estiver pronta
        import automacao.signals
