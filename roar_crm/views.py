"""
Views for the base roar_crm project.
"""
from django.shortcuts import render, redirect

def admin_disabled(request):
    """View to replace the Django admin with an informative page."""
    return render(request, 'admin_disabled.html', {
        'title': 'Administração Desativada',
        'message': 'O painel de administração do Django foi desativado para este projeto.'
    })

def home_redirect(request):
    """Redirects to the appropriate home page based on user role."""
    return redirect('main:dashboard')

def test_view(request):
    """Simple test view."""
    return render(request, 'base.html', {'title': 'Test Page'})

def simple_test_view(request):
    """Simpler test view with minimal template."""
    return render(request, 'base_minimal.html', {'title': 'Simple Test'})

def debug_test_view(request):
    """Debug test view."""
    return render(request, 'base_debug.html', {'title': 'Debug Test'})

def test_simple_standalone(request):
    """Standalone test view."""
    return render(request, 'base_minimal.html', {'title': 'Standalone Test'})
