from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('cadastrar/', views.cadastrar_lead, name='cadastrar_lead'),
    path('lista/', views.lista_leads, name='lista_leads'),
    path('<int:lead_id>/', views.detalhes_lead, name='detalhes_lead'),
    path('<int:lead_id>/editar/', views.editar_lead, name='editar_lead'),
    
    # APIs para o dashboard e outras funcionalidades
    path('api/lista/', api.leads_api_list, name='api_lista_leads'),
]
