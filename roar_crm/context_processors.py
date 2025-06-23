"""
Context processor para adicionar compatibilidade de URLs nos templates Django.
Isso permite que templates antigos que usam nomes de URLs obsoletos continuem funcionando.
"""

from django.urls import reverse, NoReverseMatch
from roar_crm.url_mappings import get_url_name, URL_MAPPINGS, NAMESPACE_MAPPINGS, RENAMED_URLS

def url_compatibility(request):
    """
    Adiciona funções de compatibilidade de URL ao contexto dos templates.
    
    Args:
        request: O objeto request do Django
        
    Returns:
        dict: Um dicionário com funções de compatibilidade de URL
    """
    def get_url(url_name, *args, **kwargs):
        """
        Função para templates que obtém uma URL, tentando a versão nova primeiro.
        Se a URL nova não existir, tenta a versão antiga.
        
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
    
    def url_exists(url_name):
        """
        Verifica se uma URL existe, tentando a versão nova primeiro.
        Se a URL nova não existir, tenta a versão antiga.
        
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
    
    # Retornar as funções no contexto
    return {
        'get_compatible_url': get_url,
        'url_exists': url_exists,
        'url_mappings': URL_MAPPINGS,
    }
