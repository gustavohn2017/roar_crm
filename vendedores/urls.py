from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_vendedor, name='dashboard_vendedor'),
    path('contato/<int:lead_id>/', views.registrar_contato, name='registrar_contato'),
    path('historico/', views.historico_contatos, name='historico_contatos'),
    path('lead/<int:lead_id>/', views.detalhes_lead, name='detalhes_lead'),
    path('logout/', views.logout_view, name='logout'),
]