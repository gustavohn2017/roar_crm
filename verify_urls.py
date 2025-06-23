"""
Verificador de URLs para o projeto Roar CRM.

Este script verifica a consistência das URLs em todo o projeto,
identificando problemas como URLs referenciadas que não existem,
padrões inconsistentes entre as aplicações e muito mais.

Executar:
- python verify_urls.py

Isso gerará um relatório com possíveis problemas encontrados.
"""

import os
import sys
import re
import django
from django.urls import reverse, NoReverseMatch
from collections import defaultdict

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roar_crm.settings')
django.setup()

# Lista de namespaces padrão
STANDARD_NAMESPACES = ['main', 'leads', 'gerencia', 'automacao']

# Padrões de URL padrão que deveriam existir em cada namespace
STANDARD_URL_PATTERNS = ['index', 'dashboard']

# Cores para terminal
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_url_exists(url_name):
    """Verifica se uma URL existe no sistema."""
    try:
        reverse(url_name)
        return True
    except NoReverseMatch:
        return False

def find_url_references_in_files(root_dir):
    """
    Encontra todas as referências a URLs nos arquivos .py e .html
    
    Retorna um dicionário com as URLs encontradas e suas localizações.
    """
    url_references = defaultdict(list)
    pattern = re.compile(r'(?:reverse|redirect|url)\s*\(\s*[\'"]([a-zA-Z0-9_:]+)[\'"]')
    template_pattern = re.compile(r'{% url [\'"]?([a-zA-Z0-9_:]+)[\'"]?')
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(('.py', '.html')):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # Procurar por padrões de URL em código Python
                        for match in pattern.finditer(content):
                            url_references[match.group(1)].append(filepath)
                        
                        # Procurar por padrões de URL em templates Django
                        if filename.endswith('.html'):
                            for match in template_pattern.finditer(content):
                                url_references[match.group(1)].append(filepath)
                except Exception as e:
                    print(f"Erro ao ler {filepath}: {e}")
                    
    return url_references

def check_standard_urls():
    """Verifica se todas as URLs padrão existem em cada namespace."""
    missing_patterns = []
    
    for namespace in STANDARD_NAMESPACES:
        for pattern in STANDARD_URL_PATTERNS:
            url_name = f"{namespace}:{pattern}"
            if not check_url_exists(url_name):
                missing_patterns.append(url_name)
    
    return missing_patterns

def check_url_references(url_references):
    """Verifica se todas as URLs referenciadas existem."""
    missing_urls = []
    
    for url in url_references.keys():
        if not check_url_exists(url):
            missing_urls.append(url)
    
    return missing_urls

def get_all_defined_urls():
    """
    Obtém todas as URLs definidas no projeto.
    Isso requer iterar pelo sistema de resolução de URLs do Django.
    """
    from django.urls import get_resolver, URLPattern, URLResolver
    
    def collect_urls(resolver, namespace=''):
        urls = []
        
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLPattern):
                if pattern.name:
                    url_name = f"{namespace}:{pattern.name}" if namespace else pattern.name
                    urls.append(url_name)
            elif isinstance(pattern, URLResolver):
                if pattern.namespace:
                    new_namespace = f"{namespace}:{pattern.namespace}" if namespace else pattern.namespace
                else:
                    new_namespace = namespace
                urls.extend(collect_urls(pattern, namespace=new_namespace))
                
        return urls
    
    resolver = get_resolver()
    return collect_urls(resolver)

def suggest_fixes(missing_url):
    """Sugere correções para URLs faltantes."""
    # Dividir a URL no namespace e nome
    if ':' in missing_url:
        namespace, name = missing_url.split(':', 1)
        
        # Verificar se o namespace existe mas o nome está errado
        if namespace in STANDARD_NAMESPACES:
            # Verificar URLs similares nesse namespace
            similar_urls = []
            defined_urls = get_all_defined_urls()
            
            for url in defined_urls:
                if url.startswith(f"{namespace}:"):
                    url_name = url.split(':', 1)[1]
                    # Verificar similaridade
                    if name in url_name or url_name in name:
                        similar_urls.append(url)
            
            if similar_urls:
                return f"URLs similares em {namespace}: {', '.join(similar_urls)}"
            else:
                return f"O namespace {namespace} existe, mas {name} não foi encontrado"
        else:
            return f"O namespace {namespace} não existe. Namespaces disponíveis: {', '.join(STANDARD_NAMESPACES)}"
    else:
        return "Formato de URL inválido, deve ser 'namespace:name'"

def main():
    """Função principal do verificador de URLs."""
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}VERIFICAÇÃO DE URLs DO PROJETO ROAR CRM{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    # Verificar URLs padrão
    print("\n1. Verificando URLs padrão...")
    missing_standards = check_standard_urls()
    
    if missing_standards:
        print(f"{YELLOW}  {len(missing_standards)} URLs padrão estão faltando:{RESET}")
        for url in missing_standards:
            print(f"  - {url}")
    else:
        print(f"{GREEN}  Todas as URLs padrão estão definidas!{RESET}")
    
    # Verificar referências de URL
    print("\n2. Procurando referências de URL no código...")
    url_references = find_url_references_in_files(os.path.dirname(os.path.dirname(__file__)))
    print(f"  {len(url_references)} URLs únicas referenciadas no código.")
    
    # Verificar se as URLs referenciadas existem
    print("\n3. Verificando se todas as URLs referenciadas existem...")
    missing_urls = check_url_references(url_references)
    
    if missing_urls:
        print(f"{RED}  {len(missing_urls)} URLs referenciadas não existem:{RESET}")
        for url in missing_urls:
            print(f"\n  - {url}")
            print(f"    Referenciada em: {', '.join(url_references[url][:3])}" + 
                  (f" e {len(url_references[url])-3} mais..." if len(url_references[url]) > 3 else ""))
            print(f"    Sugestão: {suggest_fixes(url)}")
    else:
        print(f"{GREEN}  Todas as URLs referenciadas existem!{RESET}")
    
    # Relatório final
    print(f"\n{BOLD}{'='*60}{RESET}")
    if missing_standards or missing_urls:
        print(f"{YELLOW}RELATÓRIO: Foram encontrados problemas que precisam de atenção.{RESET}")
        total_issues = len(missing_standards) + len(missing_urls)
        print(f"Total de problemas: {total_issues}")
    else:
        print(f"{GREEN}RELATÓRIO: Nenhum problema encontrado nas URLs do projeto!{RESET}")
    
    print(f"{BOLD}{'='*60}{RESET}")

if __name__ == "__main__":
    main()
