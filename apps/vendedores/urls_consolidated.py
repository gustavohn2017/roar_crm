"""
URLs consolidadas para a aplicação vendedores.
"""
from django.urls import path
from . import views_consolidated as views

app_name = 'vendedores'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_vendedor, name='dashboard'),
    
    # Contatos com leads
    path('contatar/<int:lead_id>/', views.contatar_lead, name='contatar_lead'),
    path('exportar-tentativas/', views.exportar_tentativas, name='exportar_tentativas'),
    
    # Gestão de eventos
    path('eventos/', views.eventos_list, name='eventos_list'),
    path('eventos/novo/', views.evento_create, name='evento_create'),
    path('eventos/<int:evento_id>/editar/', views.evento_edit, name='evento_edit'),
    path('eventos/<int:evento_id>/toggle/', views.evento_toggle, name='evento_toggle'),
    
    # Gestão de notas
    path('notas/', views.notas_list, name='notas_list'),
    path('notas/nova/', views.nota_create, name='nota_create'),
    path('notas/<int:nota_id>/editar/', views.nota_edit, name='nota_edit'),
    path('notas/<int:nota_id>/toggle/', views.nota_toggle, name='nota_toggle'),
    
    # APIs AJAX
    path('api/quick-evento/', views.api_quick_evento, name='api_quick_evento'),
    path('api/quick-nota/', views.api_quick_nota, name='api_quick_nota'),
]
