"""
Decorators for access control in management and other views.
"""
from functools import wraps
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Restrict access to admin users only."""
    return login_required(user_passes_test(
        lambda u: hasattr(u, 'profile') and u.profile.role == 'admin',
        login_url='/login/'
    )(view_func))


def supervisor_or_admin_required(view_func):
    """Restrict access to supervisors or admins."""
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has profile attribute
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Perfil de usuário não encontrado. Por favor, contate o administrador.')
            return redirect('vendedores:dashboard_vendedor')
          
        # Check if user is admin or supervisor
        if request.user.profile.has_role_or_higher('supervisor'):
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, 'Acesso restrito. Você não tem permissão para acessar esta página.')
            return redirect('vendedores:dashboard_vendedor')
    return _wrapped_view


def supervisor_required(view_func):
    """Restrict access to supervisor users only."""
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has profile attribute
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Perfil de usuário não encontrado. Por favor, contate o administrador.')
            return redirect('vendedores:dashboard_vendedor')
          
        # Check if user is a supervisor (not admin)
        if request.user.profile.role == 'supervisor':
            return view_func(request, *args, **kwargs)
        elif request.user.profile.role == 'admin':
            messages.info(request, 'Esta página é específica para supervisores, mas você tem acesso como administrador.')
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, 'Acesso restrito. Esta funcionalidade é apenas para supervisores.')
            return redirect('vendedores:dashboard_vendedor')
    return _wrapped_view


def vendedor_required(view_func):
    """Restrict access to sales representatives only."""
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has profile attribute
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Perfil de usuário não encontrado. Por favor, contate o administrador.')
            return redirect('login')
          
        # Check if user is a vendedor
        if request.user.profile.role == 'vendedor':
            return view_func(request, *args, **kwargs)
        else:
            messages.info(request, 'Esta funcionalidade é específica para vendedores. Redirecionando para o painel administrativo.')
            return redirect('gerencia:painel_admin')
    return _wrapped_view
