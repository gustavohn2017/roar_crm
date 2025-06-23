"""
Tags de template personalizadas para ajudar com a compatibilidade de URLs.
"""

from django import template
from django.urls import reverse, NoReverseMatch
from roar_crm.url_mappings import get_url_name

register = template.Library()

@register.simple_tag
def compat_url(url_name, *args, **kwargs):
    """
    Template tag para gerar URLs com compatibilidade.
    Tenta resolver a URL com o nome fornecido e, se falhar, tenta com um mapeamento.
    
    Uso:
        {% compat_url 'vendedores:dashboard' %}
        {% compat_url 'leads:detail' lead_id=lead.id %}
    
    Args:
        url_name (str): Nome da URL
        *args: Argumentos para a URL
        **kwargs: Keywords arguments para a URL
        
    Returns:
        str: URL gerada ou '#' se não for possível gerar
    """
    # Tentar com o nome fornecido
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        pass
    
    # Tentar com mapeamento
    new_url_name = get_url_name(url_name)
    if new_url_name != url_name:
        try:
            return reverse(new_url_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            pass
    
    # Se tudo falhar, retornar '#' para não quebrar o template
    return '#'

@register.filter
def url_exists(url_name):
    """
    Verifica se uma URL existe, tentando tanto o nome original quanto um mapeamento.
    
    Uso:
        {% if 'vendedores:dashboard'|url_exists %}
            <a href="{% compat_url 'vendedores:dashboard' %}">Dashboard</a>
        {% endif %}
    
    Args:
        url_name (str): Nome da URL
        
    Returns:
        bool: True se a URL existir, False caso contrário
    """
    # Tentar com o nome fornecido
    try:
        reverse(url_name)
        return True
    except NoReverseMatch:
        pass
    
    # Tentar com mapeamento
    new_url_name = get_url_name(url_name)
    if new_url_name != url_name:
        try:
            reverse(new_url_name)
            return True
        except NoReverseMatch:
            pass
    
    return False

@register.simple_tag
def map_url(url_name):
    """
    Retorna o mapeamento de uma URL, sem gerar a URL em si.
    Útil para depuração ou para mostrar mapeamentos.
    
    Uso:
        {% map_url 'vendedores:dashboard' %}
        
    Args:
        url_name (str): Nome da URL
        
    Returns:
        str: Nome mapeado da URL ou o próprio nome se não tiver mapeamento
    """
    return get_url_name(url_name)
