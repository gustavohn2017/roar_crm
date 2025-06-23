"""
Arquivo de URLs para o app de leads.
"""

from django.urls import path
from . import views
from django.shortcuts import redirect

app_name = 'leads'

def leads_dashboard(request):
    """Redireciona para a lista de leads como dashboard"""
    return redirect('leads:list')

urlpatterns = [
    # Rota index padrão para leads (redireciona para a lista)
    path('', leads_dashboard, name='index'),
    path('dashboard/', leads_dashboard, name='dashboard'),
    # Rotas para gerenciamento de leads
    path('list/', views.lead_list, name='list'),
    path('create/', views.lead_create, name='create'),
    path('quick-create/', views.lead_create_quick, name='create_quick'),
    path('<int:lead_id>/', views.lead_detail, name='detail'),
    path('<int:lead_id>/edit/', views.lead_edit, name='edit'),
    path('<int:lead_id>/delete/', views.lead_delete, name='delete'),
    # Rotas para comunicação
    path('<int:lead_id>/contact/', views.lead_contact, name='contact'),
    path('export/', views.lead_export, name='export'),
    # Rotas para templates de comunicação
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:template_id>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:template_id>/delete/', views.template_delete, name='template_delete'),
]
