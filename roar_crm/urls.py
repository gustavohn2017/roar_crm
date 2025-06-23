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
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from .views import (
    admin_disabled, test_view, simple_test_view,
    debug_test_view, test_simple_standalone, home_redirect
)
from . import compatibility_urls

urlpatterns = [
    # Desativado o admin do Django e substituído por uma página informativa
    # path('admin/', admin.site.urls),  # Commented out to prevent admin issues
    path('admin/', admin_disabled),
    path('test/', test_view, name='test'),  # URL de teste
    path('simple/', simple_test_view, name='simple_test'),  # URL de teste simples
    path('debug/', debug_test_view, name='debug_test'),  # URL de debug
    path('test-simple/', test_simple_standalone, name='test_simple_standalone'),  # URL de teste standalone
    path('main/', include('vendedores.urls', namespace='main')),
    path('leads/', include('leads.urls', namespace='leads')),
    path('gerencia/', include('gerencia.urls', namespace='gerencia')),
    path('automacao/', include('automacao.urls', namespace='automacao')),
    path('compatibility/', include(compatibility_urls)),
    path('', login_required(home_redirect), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
