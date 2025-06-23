from django.urls import path
from . import views
from . import api
from . import views_comunicacao

app_name = 'leads'

urlpatterns = [
    # Rotas base de leads
    path('cadastrar/', views.cadastrar_lead, name='cadastrar_lead'),
    path('lista/', views.lista_leads, name='lista_leads'),
    path('<int:lead_id>/', views.detalhes_lead, name='detalhes_lead'),
    path('<int:lead_id>/editar/', views.editar_lead, name='editar_lead'),
    
    # Novas rotas para comunicação
    path('<int:lead_id>/whatsapp/', views_comunicacao.enviar_whatsapp, name='enviar_whatsapp'),
    path('<int:lead_id>/email/', views_comunicacao.enviar_email, name='enviar_email'),
    path('<int:lead_id>/historico-contatos/', views_comunicacao.historico_contatos, name='historico_contatos'),
    path('templates/<str:tipo>/', views_comunicacao.gerenciar_templates, name='gerenciar_templates'),
    path('api/template-content/', views_comunicacao.get_template_content, name='get_template_content'),
    
    # APIs para o dashboard e outras funcionalidades
    path('api/lista/', api.leads_api_list, name='api_lista_leads'),
]
