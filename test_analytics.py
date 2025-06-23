"""
Teste do módulo de Analytics do Lions CRM
Este script verifica se o módulo analytics.py está funcionando corretamente
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

def test_analytics():
    """Testa as principais funções do módulo analytics"""
    print("Testando o módulo de analytics do Lions CRM...")
    
    # Testar métricas gerais
    print("\n1. Testando métricas gerais:")
    metrics = DashboardAnalytics.get_general_metrics()
    pprint(metrics)
    
    # Testar estatísticas diárias
    print("\n2. Testando estatísticas diárias:")
    daily_stats = DashboardAnalytics.get_daily_stats()
    print(f"Contatos hoje: {daily_stats.get('contatos_hoje', 0)}")
    print(f"Contatos últimos 7 dias: {len(daily_stats.get('contatos_ultimos_dias', []))} registros")
    
    # Testar visão geral de leads
    print("\n3. Testando visão geral de leads:")
    leads_overview = DashboardAnalytics.get_leads_overview()
    print(f"Status de leads: {len(leads_overview.get('leads_por_status', []))} categorias")
    print(f"Origens de leads: {len(leads_overview.get('leads_por_origem', []))} origens")
    
    # Testar performance dos vendedores
    print("\n4. Testando performance dos vendedores:")
    team_performance = DashboardAnalytics.get_sales_team_performance()
    print(f"Total de vendedores analisados: {len(team_performance)}")
    
    # Testar função geral que retorna todos os dados
    print("\n5. Testando função geral get_dashboard_data():")
    all_data = get_dashboard_data()
    print(f"Total de chaves nos dados: {len(all_data)}")
    print("Chaves principais disponíveis:")
    for key in all_data.keys():
        print(f" - {key}")

if __name__ == "__main__":
    test_analytics()
