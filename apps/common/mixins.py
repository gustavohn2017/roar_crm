"""
Mixins e classes base para todas as aplicações do ROAR CRM.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requer permissão de administrador."""
    
    def test_func(self):
        return self.request.user.profile.role == 'admin'
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado. Você precisa ser administrador.')
        return redirect('main:dashboard_principal')


class SupervisorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requer permissão de supervisor ou superior."""
    
    def test_func(self):
        return self.request.user.profile.has_role_or_higher('supervisor')
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado. Você precisa ser supervisor ou administrador.')
        return redirect('main:dashboard_principal')


def admin_required(function):
    """Decorator que requer permissão de administrador."""
    def check_admin(user):
        return user.profile.role == 'admin'
    
    return user_passes_test(check_admin)(login_required(function))


def supervisor_or_admin_required(function):
    """Decorator que requer permissão de supervisor ou administrador."""
    def check_role(user):
        return user.profile.has_role_or_higher('supervisor')
    
    return user_passes_test(check_role)(login_required(function))
