"""
URL configuration for roar_crm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import HttpResponse

def home_redirect(request):
    return redirect('vendedores:dashboard_vendedor')

# Função para substituir admin panel
def admin_disabled(request):
    return HttpResponse('<h1>Acesso ao painel de admin do Django está desativado</h1><p>Por favor, use o sistema de CRM para as operações administrativas.</p><a href="/">Voltar para o CRM</a>')

urlpatterns = [
    # Desativado o admin do Django e substituído por uma página informativa
    path('admin/', admin_disabled),
    path('vendedores/', include('vendedores.urls', namespace='vendedores')),
    path('leads/', include('leads.urls')),
    path('gerencia/', include('gerencia.urls', namespace='gerencia')),
    path('', login_required(home_redirect), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
]
