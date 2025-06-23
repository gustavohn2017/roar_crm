"""
Ferramenta para analisar arquivos de template em busca de URLs obsoletas
e sugerir atualizações usando o sistema de compatibilidade.

Esta ferramenta escaneia todos os templates do projeto em busca de
referências à URL usando as tags {% url %} e gera um relatório
de sugestões de correção.

Uso:
    python scan_templates_for_urls.py [--check] [--fix]
    
Opções:
    --check  Apenas verifica problemas sem modificar arquivos
    --fix    Tenta corrigir automaticamente problemas encontrados (experimental)
"""

import os
import re
import sys
import argparse
from pathlib import Path
import django
from django.urls import reverse, NoReverseMatch

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roar_crm.settings')
django.setup()

# Importar após configuração do Django
from roar_crm.url_mappings import get_url_name, URL_MAPPINGS

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

def find_template_files(base_dir=None):
    """
    Encontra todos os arquivos de template Django no projeto.
    
    Args:
        base_dir: Diretório base para iniciar a busca (opcional)
        
    Returns:
        list: Lista de caminhos para os arquivos de template
    """
    if base_dir is None:
        base_dir = Path(django.conf.settings.BASE_DIR)
    
    template_files = []
    
    # Procurar em diretórios templates/
    for template_dir in Path(base_dir).glob('**/templates/**/*.html'):
        if template_dir.is_file():
            template_files.append(template_dir)
    
    return template_files

def scan_template_for_urls(template_file):
    """
    Escaneia um arquivo de template em busca de tags {% url %}.
    
    Args:
        template_file: Caminho para o arquivo de template
        
    Returns:
        list: Lista de tuplas (url_name, linha, linha_completa)
    """
    url_references = []
    
    # Padrão para encontrar tags {% url %}
    url_pattern = re.compile(r'{%\s*url\s+[\'"]([^\'"\s]+)[\'"]')
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                for match in url_pattern.finditer(line):
                    url_name = match.group(1)
                    url_references.append((url_name, i, line.strip()))
    except Exception as e:
        print(f"Erro ao ler {template_file}: {e}")
    
    return url_references

def get_suggestion_for_url(url_name):
    """
    Gera uma sugestão para uma URL obsoleta.
    
    Args:
        url_name: Nome da URL
        
    Returns:
        tuple: (nova_url, tipo_de_solucao)
    """
    # Verificar se a URL existe
    if check_url_exists(url_name):
        return None, "OK"
    
    # Verificar se existe no mapeamento
    new_url_name = get_url_name(url_name)
    if new_url_name != url_name and check_url_exists(new_url_name):
        return new_url_name, "MAPPED"
    
    # Tentar encontrar URLs similares
    if ':' in url_name:
        namespace, name = url_name.split(':', 1)
        
        # Tentar namespaces comuns
        if namespace == 'vendedores':
            test_url = f"main:{name}"
            if check_url_exists(test_url):
                return test_url, "NAMESPACE"
        
        # Tentar variações do nome
        similar_names = []
        if namespace in ['main', 'leads', 'gerencia', 'automacao']:
            # Verificar nomes similares dentro do mesmo namespace
            for mapped_old, mapped_new in URL_MAPPINGS.items():
                if mapped_old.startswith(f"{namespace}:") and name in mapped_old:
                    similar_names.append(mapped_new)
        
        if similar_names:
            return similar_names[0], "SIMILAR"
    
    return None, "UNKNOWN"

def generate_fix(template_file, url_references):
    """
    Gera correções para as referências de URL no arquivo de template.
    
    Args:
        template_file: Caminho para o arquivo de template
        url_references: Lista de referências de URL a serem corrigidas
        
    Returns:
        str: Conteúdo corrigido do arquivo
    """
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Gerar correções
    for url_name, _, _ in url_references:
        new_url_name, solution_type = get_suggestion_for_url(url_name)
        
        if solution_type not in ["OK", "UNKNOWN"] and new_url_name:
            # Substituir a tag url simples
            pattern = re.compile(rf'{{% url [\'"]({url_name})[\'"]')
            content = pattern.sub(f"{{% load url_compat %}}{{% compat_url '{url_name}' }}", content)
            
            # Substituir a tag url com parâmetros
            pattern = re.compile(rf'{{% url [\'"]({url_name})[\'"] ([^%]+) %}}')
            content = pattern.sub(lambda m: f"{{% load url_compat %}}{{% compat_url '{url_name}' {m.group(2)} %}}", content)
    
    return content

def main():
    """Função principal do verificador de templates."""
    parser = argparse.ArgumentParser(description='Escaneia templates em busca de referências de URL obsoletas.')
    parser.add_argument('--check', action='store_true', help='Apenas verifica problemas sem modificar arquivos')
    parser.add_argument('--fix', action='store_true', help='Tenta corrigir automaticamente problemas encontrados (experimental)')
    
    args = parser.parse_args()
    
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}VERIFICAÇÃO DE URLs EM TEMPLATES DO PROJETO ROAR CRM{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    # Encontrar todos os arquivos de template
    template_files = find_template_files()
    print(f"\nEncontrados {len(template_files)} arquivos de template para análise.\n")
    
    # Estatísticas
    total_references = 0
    problematic_references = 0
    files_with_problems = 0
    files_fixed = 0
    
    # Analisar cada arquivo
    for template_file in template_files:
        url_references = scan_template_for_urls(template_file)
        total_references += len(url_references)
        
        # Verificar se há problemas
        problematic_urls = []
        for url_name, line, line_text in url_references:
            new_url_name, solution_type = get_suggestion_for_url(url_name)
            
            if solution_type != "OK":
                problematic_urls.append((url_name, line, line_text, new_url_name, solution_type))
                problematic_references += 1
        
        # Se encontrou problemas neste arquivo
        if problematic_urls:
            files_with_problems += 1
            relative_path = os.path.relpath(template_file, django.conf.settings.BASE_DIR)
            print(f"\n{YELLOW}Arquivo: {relative_path} ({len(problematic_urls)} problemas){RESET}")
            
            for url_name, line, line_text, new_url_name, solution_type in problematic_urls:
                solution_color = GREEN if solution_type in ["MAPPED", "NAMESPACE", "SIMILAR"] else RED
                print(f"  Linha {line}: {line_text}")
                
                if solution_type == "UNKNOWN":
                    print(f"  {RED}URL '{url_name}' não encontrada e sem sugestão{RESET}")
                else:
                    print(f"  {solution_color}URL '{url_name}' → '{new_url_name}' ({solution_type}){RESET}")
                
                # Sugerir correção
                if solution_type in ["MAPPED", "NAMESPACE", "SIMILAR"]:
                    old_tag = f"{{% url '{url_name}' %}}"
                    new_tag = f"{{% load url_compat %}}{{% compat_url '{url_name}' %}}"
                    print(f"  Sugestão: {old_tag} → {new_tag}")
            
            # Aplicar correção se solicitado
            if args.fix:
                try:
                    fixed_content = generate_fix(template_file, url_references)
                    
                    # Criar backup
                    backup_file = f"{template_file}.bak"
                    os.replace(template_file, backup_file)
                    
                    # Escrever arquivo corrigido
                    with open(template_file, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    files_fixed += 1
                    print(f"  {GREEN}✓ Correções aplicadas (backup em {os.path.basename(backup_file)}){RESET}")
                except Exception as e:
                    print(f"  {RED}✗ Erro ao corrigir: {e}{RESET}")
    
    # Resumo
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}RESUMO DA ANÁLISE{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"Total de arquivos analisados: {len(template_files)}")
    print(f"Total de referências de URL: {total_references}")
    
    if problematic_references > 0:
        print(f"{YELLOW}Arquivos com problemas: {files_with_problems}{RESET}")
        print(f"{YELLOW}Referências problemáticas: {problematic_references}{RESET}")
        
        if args.fix:
            print(f"{GREEN}Arquivos corrigidos: {files_fixed}{RESET}")
        elif not args.check:
            print(f"\nPara tentar corrigir automaticamente, execute com a opção --fix:")
            print(f"python scan_templates_for_urls.py --fix")
    else:
        print(f"{GREEN}Nenhum problema encontrado!{RESET}")

if __name__ == "__main__":
    main()
