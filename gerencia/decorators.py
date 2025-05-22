"""
Decoradores para controle de acesso nas views do módulo de gerência.
"""
from functools import wraps
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Restringe o acesso apenas para usuários administradores (is_staff=True)."""
    return login_required(user_passes_test(lambda u: u.is_staff, login_url='/login/')(view_func))

def supervisor_or_admin_required(view_func):
    """Restringe o acesso para usuários supervisores ou administradores."""
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verifica se o usuário tem o atributo profile
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Perfil de usuário não encontrado. Por favor, contate o administrador.')
            return redirect('dashboard_vendedor')
        
        # Verifica se é admin ou supervisor
        if request.user.is_staff or request.user.profile.role == 'supervisor':
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, 'Acesso restrito. Você não tem permissão para acessar esta página.')
            return redirect('dashboard_vendedor')
    return _wrapped_view


def supervisor_required(view_func):
    """Restringe o acesso apenas para usuários com função de supervisor."""
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verifica se o usuário tem o atributo profile
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Perfil de usuário não encontrado. Por favor, contate o administrador.')
            return redirect('dashboard_vendedor')
        
        # Verifica se é supervisor (não admin)
        if request.user.profile.role == 'supervisor' and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        elif request.user.is_staff:
            messages.info(request, 'Esta página é específica para supervisores, mas você tem acesso como administrador.')
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, 'Acesso restrito. Esta funcionalidade é apenas para supervisores.')
            return redirect('dashboard_vendedor')
    return _wrapped_view
