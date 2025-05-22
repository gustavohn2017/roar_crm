from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'gerencia'

urlpatterns = [
    path('', lambda request: redirect('gerencia:painel_admin'), name='index'),
    path('painel/', views.painel_admin, name='painel_admin'),
    path('vendedores/', views.vendedores, name='vendedores'),
    path('funcionarios/', views.funcionarios, name='funcionarios'),  # Mantido para compatibilidade
    path('funcionarios/cadastrar/', views.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('funcionarios/<int:user_id>/', views.detalhes_funcionario, name='detalhes_funcionario'),
    path('funcionarios/excluir/<int:user_id>/', views.excluir_funcionario, name='excluir_funcionario'),
      # URL para relatório de desempenho (acessível para supervisores)
    path('desempenho/', views.relatorio_desempenho, name='relatorio_desempenho'),
    
    # Novas URLs para exportação de dados
    path('funcionarios/exportar/', views.exportar_funcionarios, name='exportar_funcionarios'),
    path('contatos/exportar/', views.exportar_contatos, name='exportar_contatos'),
    path('contatos/exportar/<int:user_id>/', views.exportar_contatos, name='exportar_contatos_funcionario'),
    path('leads/exportar/', views.exportar_leads, name='exportar_leads'),
]
