from django.urls import path, include
from . import views

app_name = 'automacao'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_automacao, name='index'),
    path('dashboard/', views.dashboard_automacao, name='dashboard'),
    path('executar/', views.executar_automacao, name='executar_automacao'),
    
    # Lead Scoring
    path('lead-scoring/', views.lead_scoring_dashboard, name='lead_scoring_list'),
    path('lead-scoring/recalcular/', views.recalcular_scores, name='recalcular_scores'),
    
    # Workflows
    path('workflows/', views.lista_workflows, name='workflow_list'),
    path('workflows/create/', views.criar_workflow, name='workflow_create'),
    path('workflows/<int:workflow_id>/update/', views.editar_workflow, name='workflow_update'),
    path('workflows/<int:workflow_id>/acoes/create/', views.adicionar_acao_workflow, name='acao_workflow_create'),
    
    # Campanhas de Nutrição
    path('campanhas/', views.lista_campanhas, name='campanha_list'),
    path('campanhas/create/', views.criar_campanha, name='campanha_create'),
    path('campanhas/<int:campanha_id>/update/', views.editar_campanha, name='campanha_update'),    # Gatilhos Automáticos
    path('gatilhos/', views.lista_gatilhos, name='gatilho_list'),
    path('gatilhos/create/', views.criar_gatilho, name='gatilho_create'),
    path('gatilhos/<int:gatilho_id>/update/', views.editar_gatilho, name='gatilho_update'),
    path('gatilhos/<int:gatilho_id>/toggle/', views.toggle_gatilho, name='gatilho_toggle'),
      # Histórico
    path('historico/', views.historico_automacao, name='historico_list'),
    
    # Execuções de Workflows
    path('execucoes/', views.listar_execucoes, name='execucao_list'),
      # APIs AJAX
    path('api/score-lead/<int:lead_id>/', views.api_score_lead, name='api_score_lead'),
    path('api/executar-workflow/<int:workflow_id>/', views.api_executar_workflow, name='api_executar_workflow'),
    path('api/adicionar-leads-campanha/<int:campanha_id>/', views.api_adicionar_leads_campanha, name='api_adicionar_leads_campanha'),
]
