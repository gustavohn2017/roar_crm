from django.urls import path, include
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.dashboard_vendedor, name='dashboard_principal'),
    path('', views.dashboard_vendedor, name='index'),  # Adicionando URL padrão 'index'
    path('dashboard/', views.dashboard_vendedor, name='dashboard_principal_alt'),
    # Alias para manter compatibilidade com outros códigos que possam usar 'dashboard'
    path('dashboard/', views.dashboard_vendedor, name='dashboard'),
    
    path('contato/<int:lead_id>/', views.registrar_contato, name='registrar_contato'),
    path('historico/', views.historico_contatos, name='historico_contatos'),
    path('lead/<int:lead_id>/', views.detalhes_lead, name='detalhes_lead'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints para o dashboard
    path('api/leads/', views.api_leads_disponiveis, name='api_leads_disponiveis'),
    
    # Novas rotas para funcionalidades utilitárias
    path('utils/calendario/', views.calendario_view, name='calendario'),
    path('utils/calendario/evento/criar/', views.criar_evento, name='criar_evento'),
    path('utils/calendario/evento/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('utils/calendario/evento/<int:evento_id>/excluir/', views.excluir_evento, name='excluir_evento'),
    path('utils/calendario/evento/<int:evento_id>/toggle/', views.toggle_evento_concluido, name='toggle_evento_concluido'),
    
    path('utils/notas/', views.notas_view, name='notas'),
    path('utils/notas/criar/', views.criar_nota, name='criar_nota'),
    path('utils/notas/<int:nota_id>/editar/', views.editar_nota, name='editar_nota'),
    path('utils/notas/<int:nota_id>/excluir/', views.excluir_nota, name='excluir_nota'),    
    path('utils/notas/<int:nota_id>/toggle/', views.toggle_nota_concluida, name='toggle_nota_concluida'),
    
    path('utils/calculadoras/', views.calculadoras_view, name='calculadoras'),
    path('utils/calculadoras/gerar-proposta/', views.gerar_proposta_pdf, name='gerar_proposta_pdf'),
    
    # Adicionando a rota para o funil de vendas
    path('utils/funnel/', views.funil_vendas_view, name='funil_vendas'),
]