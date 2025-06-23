#!/usr/bin/env python
"""
Script para corrigir problemas de estrutura nos modelos da aplicação leads.
Este script reorganiza a ordem das definições de classes e garante que
as referências entre modelos sejam válidas.
"""

import os
import shutil
from datetime import datetime

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_DIR = os.path.join(BASE_DIR, 'leads')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups', f'leads_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}')


def create_backup():
    """Cria backup dos arquivos que serão modificados."""
    print("Criando backup dos arquivos...")
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # Arquivos a serem modificados
    files_to_backup = ['models.py', 'admin.py']
    
    for file in files_to_backup:
        src = os.path.join(LEADS_DIR, file)
        if os.path.exists(src):
            dst = os.path.join(BACKUP_DIR, file)
            shutil.copy2(src, dst)
            print(f"  - Backup de {file} criado")
    
    print("Backup concluído.")


def fix_models():
    """Corrige a ordem das definições de classes nos modelos."""
    print("Corrigindo arquivo models.py...")
    
    # Ler o conteúdo do arquivo models.py
    models_path = os.path.join(LEADS_DIR, 'models.py')
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Identificar e reorganizar as classes
    # Extrair as classes principais para garantir que TemplateComunitacao 
    # seja definida antes de HistoricoContato
    lead_class = extract_class(content, 'class Lead')
    template_class = extract_class(content, 'class TemplateComunitacao')
    historico_class = extract_class(content, 'class HistoricoContato')
    
    # Criar o novo conteúdo reorganizado
    imports = extract_imports(content)
    new_content = f"""{imports}

{lead_class}

{template_class}

{historico_class}
"""
    
    # Salvar o arquivo com o conteúdo reorganizado
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Arquivo models.py corrigido com sucesso.")


def fix_admin():
    """Corrige as importações no arquivo admin.py."""
    print("Corrigindo arquivo admin.py...")
    
    # Ler o conteúdo do arquivo admin.py
    admin_path = os.path.join(LEADS_DIR, 'admin.py')
    with open(admin_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Garantir que os modelos sejam importados corretamente
    new_content = content
    if 'from .models import' in content:
        new_content = content.replace(
            'from .models import TemplateComunitacao, HistoricoContato, Lead',
            'from .models import Lead, TemplateComunitacao, HistoricoContato'
        )
    
    # Salvar o arquivo com as importações corrigidas
    with open(admin_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Arquivo admin.py corrigido com sucesso.")


def extract_class(content, class_signature):
    """Extrai uma classe completa do conteúdo."""
    start_index = content.find(class_signature)
    if start_index == -1:
        return ""
    
    # Encontra o fim da classe (próxima classe ou fim do arquivo)
    next_class = content.find('class ', start_index + len(class_signature))
    if next_class == -1:
        return content[start_index:]
    else:
        # Recuar para encontrar o último caractere da classe atual
        end_index = content.rfind('\n\n', start_index, next_class)
        if end_index == -1:
            end_index = next_class
        return content[start_index:end_index]


def extract_imports(content):
    """Extrai as declarações de importação do início do arquivo."""
    import_end = 0
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith(('import', 'from', '#', '"""', "'''", ' ')):
            import_end = i
            break
    
    return '\n'.join(lines[:import_end])


def main():
    print("=== Correção de Estrutura de Modelos ===")
    choice = input("Esta operação corrigirá problemas de estrutura nos modelos da aplicação leads. Deseja continuar? [s/N]: ")
    
    if choice.lower() != 's':
        print("Operação cancelada.")
        return
    
    create_backup()
    fix_models()
    fix_admin()
    
    print("\n=== Correção concluída com sucesso! ===")
    print("Os arquivos foram reorganizados para garantir que as referências entre modelos sejam válidas.")
    print(f"Um backup dos arquivos originais foi criado em: {BACKUP_DIR}")
    print("\nAgora tente executar o servidor Django:")
    print("  python manage.py runserver")


if __name__ == "__main__":
    main()
