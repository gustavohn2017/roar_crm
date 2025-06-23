"""
URL patterns for the management application.
"""
from django.urls import path
from django.shortcuts import redirect
from . import views_consolidated as views

app_name = 'management'

urlpatterns = [
    # Main dashboard redirects to admin panel
    path('', lambda request: redirect('management:painel_admin'), name='index'),
    
    # Administrative panels
    path('painel/', views.painel_admin, name='painel_admin'),
    path('vendedores/', views.vendedores_list, name='vendedores'),
    
    # User management
    path('funcionarios/', views.funcionarios_list, name='funcionarios'),
    path('funcionarios/cadastrar/', views.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('funcionarios/<int:user_id>/', views.detalhes_funcionario, name='detalhes_funcionario'),
    path('funcionarios/editar/<int:user_id>/', views.editar_funcionario, name='editar_funcionario'),
    path('funcionarios/excluir/<int:user_id>/', views.excluir_funcionario, name='excluir_funcionario'),
    
    # User profile
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/senha/', views.alterar_senha, name='alterar_senha'),
    
    # Reports
    path('desempenho/', views.relatorio_desempenho, name='relatorio_desempenho'),
    
    # Data export
    path('funcionarios/exportar/', views.exportar_funcionarios, name='exportar_funcionarios'),
    path('contatos/exportar/', views.exportar_contatos, name='exportar_contatos'),
    path('contatos/exportar/<int:user_id>/', views.exportar_contatos, name='exportar_contatos_funcionario'),
    path('leads/exportar/', views.exportar_leads, name='exportar_leads'),
]
