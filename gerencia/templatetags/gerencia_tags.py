from django import template
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def format_percent(value):
    """Formata um valor decimal como porcentagem"""
    if value is None:
        return "0%"
    return f"{value:.1f}%"

@register.filter
def status_badge_class(status):
    """Retorna a classe CSS do Bootstrap para o status do lead"""
    classes = {
        'novo': 'bg-info',
        'contatado': 'bg-secondary',
        'qualificado': 'bg-primary',
        'proposta': 'bg-warning',
        'negociacao': 'bg-warning',
        'fechado': 'bg-success',
        'perdido': 'bg-danger',
    }
    return classes.get(status, 'bg-secondary')

@register.filter
def resultado_contato_badge_class(resultado):
    """Retorna a classe CSS do Bootstrap para o resultado do contato"""
    classes = {
        'sucesso': 'badge-success',
        'nao_atendeu': 'badge-warning',
        'ocupado': 'badge-info',
        'numero_invalido': 'badge-danger',
        'outro': 'badge-secondary',
    }
    return classes.get(resultado, 'badge-secondary')

@register.filter
def time_since(date):
    """Retorna o tempo decorrido desde uma data até agora em formato legível"""
    if not date:
        return "Nunca"
    
    now = timezone.now()
    diff = now - date
    
    if diff < timedelta(minutes=1):
        return "agora mesmo"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"há {minutes} {'minuto' if minutes == 1 else 'minutos'}"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"há {hours} {'hora' if hours == 1 else 'horas'}"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"há {days} {'dia' if days == 1 else 'dias'}"
    elif diff < timedelta(days=365):
        months = diff.days // 30
        return f"há {months} {'mês' if months == 1 else 'meses'}"
    else:
        years = diff.days // 365
        return f"há {years} {'ano' if years == 1 else 'anos'}"

@register.filter
def subtract(value, arg):
    """Subtracts the arg from the value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def filter_active(queryset):
    """Filters queryset by is_active=True"""
    return [item for item in queryset if item.is_active]

@register.filter
def filter_inactive(queryset):
    """Filters queryset by is_active=False"""
    return [item for item in queryset if not item.is_active]

# Novas template tags para verificação de permissões baseadas em função

@register.filter
def is_admin(user):
    """Verifica se o usuário é um administrador"""
    return user.is_authenticated and user.is_staff

@register.filter
def is_supervisor(user):
    """Verifica se o usuário é um supervisor"""
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'supervisor'

@register.filter
def is_vendedor(user):
    """Verifica se o usuário é um vendedor"""
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'vendedor'

@register.filter
def is_admin_or_supervisor(user):
    """Verifica se o usuário é um administrador ou supervisor"""
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'supervisor'

@register.filter
def has_role_or_higher(user, required_role):
    """Verifica se o usuário tem o papel especificado ou superior"""
    role_hierarchy = {
        'vendedor': 0,
        'supervisor': 1,
        'admin': 2
    }
    
    if not user.is_authenticated:
        return False
    
    # Admins têm acesso a tudo
    if user.is_staff:
        return True
    
    if not hasattr(user, 'profile'):
        return False
    
    user_role = user.profile.role
    user_level = role_hierarchy.get(user_role, -1)
    required_level = role_hierarchy.get(required_role, 999)
    
    return user_level >= required_level
