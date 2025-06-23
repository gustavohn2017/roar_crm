"""
Teste básico do módulo de Analytics do Lions CRM
"""
import os
import sys
import django
from pprint import pprint

# Configurar o ambiente Django
sys.path.append('.')  # Adicionar o diretório atual ao PATH
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roar_crm.settings')
django.setup()

# Importar o módulo de analytics
from gerencia.analytics import DashboardAnalytics, get_dashboard_data

def test_basic_analytics():
    """Testa apenas as funções básicas do módulo analytics"""
    print("Testando funções básicas do módulo analytics...")
    
    # Testar métricas gerais
    print("\n1. Métricas gerais:")
    metrics = DashboardAnalytics.get_general_metrics()
    pprint(metrics)
    
    # Testar estatísticas diárias
    print("\n2. Estatísticas diárias:")
    daily_stats = DashboardAnalytics.get_daily_stats()
    print(f"Contatos hoje: {daily_stats.get('contatos_hoje', 0)}")
    
    # Formatação para gráficos
    print("\n3. Formatação para gráficos:")
    formatted = DashboardAnalytics.format_for_charts({
        'teste_numero': 42,
        'teste_lista': [{'valor': 1}, {'valor': 2}]
    })
    pprint(formatted)

if __name__ == "__main__":
    test_basic_analytics()
