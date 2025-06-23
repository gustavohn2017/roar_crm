"""
Script para atualizar referências aos arquivos de leads consolidados.
Este script deve ser executado após a consolidação dos arquivos para
garantir que todas as referências no projeto estejam apontando para
os arquivos consolidados.
"""

import os
import re
import sys
from pathlib import Path

# Determinar o caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent

# Definir os padrões de substituição
REPLACEMENT_PATTERNS = [
    # Para modelos
    (r'from\s+leads\.models(?:_new)?\s+import', 'from leads.models_consolidated import'),
    (r'from\s+leads\.models_comunicacao\s+import', 'from leads.models_consolidated import'),
    
    # Para forms
    (r'from\s+leads\.forms(?:_new)?\s+import', 'from leads.forms_consolidated import'),
    (r'from\s+leads\.forms_comunicacao\s+import', 'from leads.forms_consolidated import'),
    
    # Para views
    (r'from\s+leads\s+import\s+views(?:_new)?(?:\s+as\s+views)?', 'from leads import views_consolidated as views'),
    (r'from\s+leads\.views(?:_new)?\s+import', 'from leads.views_consolidated import'),
    (r'from\s+leads\.views_comunicacao\s+import', 'from leads.views_consolidated import'),
    
    # Para admin
    (r'from\s+leads\.admin(?:_new)?\s+import', 'from leads.admin_consolidated import'),
    
    # Para urls
    (r'path\([\'"]leads/[\'"],\s*include\([\'"]leads\.urls(?:_new)?[\'"]', 'path(\'leads/\', include(\'leads.urls_consolidated\''),
]

def should_process_file(file_path):
    """Verifica se o arquivo deve ser processado."""
    # Ignorar arquivos consolidados
    if any(x in file_path for x in ['_consolidated', '.git', '__pycache__', '.pyc']):
        return False
    
    # Processar apenas arquivos Python
    return file_path.endswith('.py')

def update_imports(file_path):
    """Atualiza as importações em um arquivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # Aplicar padrões de substituição
        for pattern, replacement in REPLACEMENT_PATTERNS:
            content = re.sub(pattern, replacement, content)
        
        # Verificar se houve alterações
        if content != original_content:
            print(f"Atualizando: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False

def walk_directory(directory):
    """Percorre o diretório recursivamente."""
    updated_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if should_process_file(file_path):
                    if update_imports(file_path):
                        updated_files += 1
    
    return updated_files

def main():
    print("Iniciando atualização de referências...")
    
    updated_files = walk_directory(BASE_DIR)
    
    print(f"Concluído! {updated_files} arquivos foram atualizados.")
    print("Recomenda-se verificar se o sistema está funcionando corretamente.")

if __name__ == "__main__":
    main()
