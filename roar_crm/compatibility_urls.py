"""
Arquivo centralizado para compatibilidade de URLs.

Este arquivo consolida todos os redirecionamentos de URLs antigas para novas em um único local,
facilitando a manutenção e garantindo a consistência em todo o projeto.
"""

from roar_crm.url_compatibility import CompatibilityRouter

# Router para a aplicação 'vendedores' (anteriormente 'main')
router_vendedores = CompatibilityRouter('vendedores')
router_vendedores.add_redirect('home/', 'dashboard')
router_vendedores.add_redirect('painel/', 'dashboard')
router_vendedores.add_redirect('contatos/historico/', 'historico_contatos')
router_vendedores.add_redirect('agenda/', 'calendario')
router_vendedores.add_redirect('lembretes/', 'notas')
router_vendedores.add_redirect('tarefas/', 'notas')
router_vendedores.add_redirect('calculadora/', 'calculadoras')
router_vendedores.add_redirect('funil/', 'funil_vendas')
router_vendedores.add_redirect('dashboard_vendedor/', 'dashboard')
router_vendedores.add_redirect('inicio/', 'dashboard')
router_vendedores.add_redirect('eventos/', 'calendario')
router_vendedores.add_redirect('calendario/eventos/', 'calendario')

# Router para a aplicação 'gerencia'
router_gerencia = CompatibilityRouter('gerencia')
router_gerencia.add_redirect('painel-controle/', 'painel_admin')
router_gerencia.add_redirect('equipe/', 'vendedores')
router_gerencia.add_redirect('usuarios/', 'funcionarios')
router_gerencia.add_redirect('relatorios/', 'relatorio_desempenho')
router_gerencia.add_redirect('dash/', 'dashboard')

# Router para a aplicação 'automacao'
router_automacao = CompatibilityRouter('automacao')
router_automacao.add_redirect('painel/', 'dashboard')
router_automacao.add_redirect('workflow/', 'workflow_list')
router_automacao.add_redirect('campanha/', 'campanha_list')
router_automacao.add_redirect('gatilho/', 'gatilho_list')
router_automacao.add_redirect('scoring/', 'lead_scoring_list')
router_automacao.add_redirect('workflows/', 'workflow_list')
router_automacao.add_redirect('campanhas/', 'campanha_list')
router_automacao.add_redirect('gatilhos/', 'gatilho_list')
router_automacao.add_redirect('score/', 'lead_scoring_list')

# Agrupar todos os urlpatterns de compatibilidade
urlpatterns = (
    router_vendedores.get_urlpatterns() +
    router_gerencia.get_urlpatterns() +
    router_automacao.get_urlpatterns()
)
