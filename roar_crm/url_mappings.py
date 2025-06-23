"""
Mapeamento central de compatibilidade de URLs para o sistema Roar CRM.

Este arquivo fornece mapeamentos para URLs antigas que podem estar sendo referenciadas
em diferentes partes do sistema. Ele serve como um ponto central para gerenciar
redirecionamentos de URLs obsoletas para as novas.

Uso:
    Em qualquer view, pode-se importar e usar:
    from roar_crm.url_mappings import get_url_name

    # Depois usar:
    url = get_url_name('vendedores:dashboard')  # Retorna 'main:dashboard'
"""

from django.urls import reverse, NoReverseMatch

# Mapeamentos de namespaces antigos para novos
NAMESPACE_MAPPINGS = {
    'vendedores': 'main',
    'management': 'gerencia',
}

# Mapeamentos de URLs específicas (formato: 'namespace_antigo:nome_antigo': 'namespace_novo:nome_novo')
URL_MAPPINGS = {
    # Mapeamentos vendedores -> main
    'vendedores:dashboard': 'main:dashboard',
    'vendedores:dashboard_vendedor': 'main:dashboard',
    'vendedores:eventos_list': 'main:calendario',
    'vendedores:notas_list': 'main:notas',
    
    # Mapeamentos management -> gerencia
    'management:painel_admin': 'gerencia:painel_admin',
    'management:funcionarios': 'gerencia:funcionarios',
    'management:detalhes_funcionario': 'gerencia:detalhes_funcionario',
    'management:perfil': 'gerencia:painel_admin',  # Assumindo que não existe perfil específico
    
    # URLs sem namespace (formato incorreto)
    'detalhes_lead': 'leads:detail',
    'historico_contatos': 'main:historico_contatos',
    'lista_leads': 'leads:list',
    'dashboard_vendedor': 'main:dashboard',
    'calendario': 'main:calendario',
    'calculadoras': 'main:calculadoras',
    'notas': 'main:notas',
    'relatorios': 'gerencia:relatorio_desempenho',
    'exportar_dados': 'gerencia:exportar_funcionarios',
    'quick_lead': 'leads:create_quick',
    'criar_nota': 'main:criar_nota',
    'editar_nota': 'main:editar_nota', 
    'toggle_nota_concluida': 'main:toggle_nota_concluida',
    'excluir_nota': 'main:excluir_nota',
}

# URLs que foram renomeadas dentro do mesmo namespace
RENAMED_URLS = {
    'leads:edit': 'leads:edit',  # Na verdade não mudou, mas está referenciada incorretamente em alguns lugares
    'automacao:lead_scoring_dashboard': 'automacao:lead_scoring_list',
    'automacao:editar_workflow': 'automacao:workflow_update',
    'automacao:editar_campanha': 'automacao:campanha_update',
    'automacao:editar_gatilho': 'automacao:gatilho_update',
    'automacao:historico': 'automacao:historico_list',
}

def get_url_name(old_url_name):
    """
    Retorna o novo nome de URL correspondente ao nome antigo.
    Se o nome antigo não estiver mapeado, retorna o próprio nome.
    
    Args:
        old_url_name (str): Nome antigo da URL (formato 'namespace:nome')
        
    Returns:
        str: Nome novo da URL
    """
    # Verificar se existe um mapeamento direto
    if old_url_name in URL_MAPPINGS:
        return URL_MAPPINGS[old_url_name]
    
    # Se não tem : é uma URL sem namespace
    if ':' not in old_url_name:
        return old_url_name
    
    # Verificar se é um URL renomeada dentro do mesmo namespace
    if old_url_name in RENAMED_URLS:
        return RENAMED_URLS[old_url_name]
    
    # Separar namespace e nome
    try:
        namespace, name = old_url_name.split(':', 1)
    except ValueError:
        return old_url_name
    
    # Verificar se o namespace foi mapeado
    if namespace in NAMESPACE_MAPPINGS:
        new_namespace = NAMESPACE_MAPPINGS[namespace]
        new_url_name = f"{new_namespace}:{name}"
        
        # Tentar resolver a URL para ver se existe
        try:
            reverse(new_url_name)
            return new_url_name
        except NoReverseMatch:
            pass
    
    # Se não encontrou mapeamento, retorna o nome original
    return old_url_name

def get_compatible_url(request, old_url_name, **kwargs):
    """
    Gera uma URL compatível, redirecionando para a versão mais nova.
    
    Args:
        request: Request do Django
        old_url_name (str): Nome antigo da URL
        **kwargs: Parâmetros para a URL
        
    Returns:
        str: URL gerada
    """
    new_url_name = get_url_name(old_url_name)
    
    try:
        return reverse(new_url_name, kwargs=kwargs)
    except NoReverseMatch:
        # Tentar sem os parâmetros
        try:
            return reverse(new_url_name)
        except NoReverseMatch:
            # Se tudo falhar, voltar para a home
            return reverse('home')
