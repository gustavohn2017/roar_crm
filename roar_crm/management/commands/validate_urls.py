"""
Comando de gerenciamento Django para validar e corrigir problemas de URL.

Este comando analisa o projeto em busca de referências de URL e identifica
problemas de compatibilidade.

Uso:
    python manage.py validate_urls [--check] [--fix-templates] [--verbose]
"""

import os
import re
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.urls import reverse, NoReverseMatch, get_resolver, URLPattern, URLResolver

from roar_crm.url_mappings import get_url_name, URL_MAPPINGS, NAMESPACE_MAPPINGS


class Command(BaseCommand):
    help = 'Valida e corrige problemas de URL no projeto'

    def add_arguments(self, parser):
        """Adiciona argumentos de linha de comando para o comando."""
        parser.add_argument(
            '--check',
            action='store_true',
            help='Apenas verifica problemas sem modificar arquivos',
        )
        parser.add_argument(
            '--fix-templates',
            action='store_true',
            help='Tenta corrigir automaticamente problemas encontrados em templates (experimental)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas sobre as verificações',
        )

    def handle(self, *args, **options):
        """
        Execução principal do comando.
        
        Args:
            *args: Argumentos posicionais
            **options: Opções de linha de comando
        """
        self.verbose = options['verbose']
        self.check_only = options['check']
        self.fix_templates = options['fix_templates']
        
        self.stdout.write(self.style.NOTICE("\n=== Validação de URLs do Projeto ===\n"))
        
        # Verificar URLs padrão
        self.stdout.write("1. Verificando URLs padrão...")
        missing_standards = self.check_standard_urls()
        
        if missing_standards:
            self.stdout.write(
                self.style.WARNING(f"  {len(missing_standards)} URLs padrão estão faltando:")
            )
            for url in missing_standards:
                self.stdout.write(f"  - {url}")
        else:
            self.stdout.write(self.style.SUCCESS("  Todas as URLs padrão estão definidas!"))
        
        # Verificar referências de URL
        self.stdout.write("\n2. Procurando referências de URL no código...")
        url_references = self.find_url_references_in_files()
        self.stdout.write(f"  {len(url_references)} URLs únicas referenciadas no código.")
        
        # Verificar se as URLs referenciadas existem
        self.stdout.write("\n3. Verificando se todas as URLs referenciadas existem...")
        missing_urls = self.check_url_references(url_references)
        
        if missing_urls:
            self.stdout.write(
                self.style.ERROR(f"  {len(missing_urls)} URLs referenciadas não existem:")
            )
            for url in missing_urls:
                self.stdout.write(f"\n  - {url}")
                self.stdout.write(
                    f"    Referenciada em: {', '.join(url_references[url][:3])}" + 
                    (f" e {len(url_references[url])-3} mais..." if len(url_references[url]) > 3 else "")
                )
                self.stdout.write(f"    Sugestão: {self.suggest_fixes(url)}")
        else:
            self.stdout.write(self.style.SUCCESS("  Todas as URLs referenciadas existem!"))
        
        # Se solicitado, também verificar templates
        if options['fix_templates']:
            import django
            from pathlib import Path
            
            self.stdout.write("\n4. Verificando e corrigindo templates...")
            
            from django.conf import settings
            base_dir = Path(settings.BASE_DIR)
            
            # Encontrar templates
            template_files = []
            for template_dir in Path(base_dir).glob('**/templates/**/*.html'):
                if template_dir.is_file():
                    template_files.append(template_dir)
                    
            self.stdout.write(f"  Encontrados {len(template_files)} templates.")
            
            # Importar e executar a ferramenta de verificação de templates
            self.stdout.write("  Executando verificador de templates...")
            
            # Importar dinamicamente o módulo (sem executá-lo como script)
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "scan_templates_for_urls", 
                os.path.join(settings.BASE_DIR, "scan_templates_for_urls.py")
            )
            template_scanner = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(template_scanner)
            
            # Configurar e executar
            template_scanner.main()
        
        # Resumo final
        self.stdout.write("\n=== Resumo ===")
        total_issues = len(missing_standards) + len(missing_urls)
        
        if total_issues > 0:
            self.stdout.write(
                self.style.WARNING(f"Total de problemas: {total_issues}")
            )
            self.stdout.write(
                "Execute 'python verify_urls.py' para uma análise mais detalhada."
            )
        else:
            self.stdout.write(self.style.SUCCESS("Nenhum problema encontrado!"))

    def check_url_exists(self, url_name):
        """Verifica se uma URL existe no sistema."""
        try:
            reverse(url_name)
            return True
        except NoReverseMatch:
            return False

    def check_standard_urls(self):
        """Verifica se todas as URLs padrão existem em cada namespace."""
        # Lista de namespaces padrão
        standard_namespaces = ['main', 'leads', 'gerencia', 'automacao']
        
        # Padrões de URL padrão que deveriam existir em cada namespace
        standard_url_patterns = ['index', 'dashboard']
        
        missing_patterns = []
        
        for namespace in standard_namespaces:
            for pattern in standard_url_patterns:
                url_name = f"{namespace}:{pattern}"
                if not self.check_url_exists(url_name):
                    missing_patterns.append(url_name)
        
        return missing_patterns

    def find_url_references_in_files(self):
        """
        Encontra todas as referências a URLs nos arquivos .py
        
        Returns:
            dict: Um dicionário com as URLs encontradas e suas localizações.
        """
        url_references = defaultdict(list)
        pattern = re.compile(r'(?:reverse|redirect|url)\s*\(\s*[\'"]([a-zA-Z0-9_:]+)[\'"]')
        
        from django.conf import settings
        base_dir = settings.BASE_DIR
        
        for dirpath, _, filenames in os.walk(base_dir):
            for filename in filenames:
                if filename.endswith('.py'):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            content = file.read()
                            for match in pattern.finditer(content):
                                url_references[match.group(1)].append(filepath)
                    except Exception as e:
                        if self.verbose:
                            self.stdout.write(f"Erro ao ler {filepath}: {e}")
                    
        return url_references

    def check_url_references(self, url_references):
        """Verifica se todas as URLs referenciadas existem."""
        missing_urls = []
        
        for url in url_references.keys():
            if not self.check_url_exists(url):
                missing_urls.append(url)
        
        return missing_urls

    def suggest_fixes(self, missing_url):
        """Sugere correções para URLs faltantes."""
        # Dividir a URL no namespace e nome
        if ':' not in missing_url:
            return "Formato de URL inválido, deve ser 'namespace:name'"
            
        namespace, name = missing_url.split(':', 1)
        
        # Verificar se o namespace existe mas o nome está errado
        standard_namespaces = ['main', 'leads', 'gerencia', 'automacao']
        
        if namespace in standard_namespaces:
            # Verificar URLs similares nesse namespace
            similar_urls = []
            
            # Obter todas as URLs definidas
            all_urls = self.get_all_defined_urls()
            
            for url in all_urls:
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
            return f"O namespace {namespace} não existe. Namespaces disponíveis: {', '.join(standard_namespaces)}"

    def get_all_defined_urls(self):
        """
        Obtém todas as URLs definidas no projeto.
        """
        urls = []
        
        def collect_urls(resolver, namespace=''):
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
                    collect_urls(pattern, namespace=new_namespace)
        
        resolver = get_resolver()
        collect_urls(resolver)
        return urls
