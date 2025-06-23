"""
Script para remover arquivos duplicados após a consolidação.
IMPORTANTE: Execute este script apenas após verificar que tudo está
funcionando corretamente com os arquivos consolidados.
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Determinar o caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent
LEADS_DIR = BASE_DIR / 'leads'
BACKUP_DIR = BASE_DIR / 'backups' / f'leads_consolidation_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

# Arquivos que serão removidos
FILES_TO_REMOVE = [
    # Arquivos originais de models
    'leads/models.py',
    'leads/models_new.py',
    'leads/models_comunicacao.py.disabled',
    
    # Arquivos originais de forms
    'leads/forms.py',
    'leads/forms_new.py',
    'leads/forms_comunicacao.py.disabled',
    
    # Arquivos originais de views
    'leads/views.py',
    'leads/views_new.py',
    'leads/views_comunicacao.py.disabled',
    
    # Arquivos originais de urls
    'leads/urls.py',
    'leads/urls_new.py',
    
    # Arquivos originais de admin
    'leads/admin.py',
    'leads/admin_new.py',
]

# Arquivos consolidados que devem ser renomeados
FILES_TO_RENAME = {
    'leads/models_consolidated.py': 'leads/models.py',
    'leads/forms_consolidated.py': 'leads/forms.py',
    'leads/views_consolidated.py': 'leads/views.py',
    'leads/urls_consolidated.py': 'leads/urls.py',
    'leads/admin_consolidated.py': 'leads/admin.py',
}

def backup_files():
    """Cria um backup dos arquivos antes de removê-los."""
    print(f"Criando backup em: {BACKUP_DIR}")
    
    # Criar o diretório de backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Backup do diretório leads
    leads_backup_dir = BACKUP_DIR / 'leads'
    shutil.copytree(LEADS_DIR, leads_backup_dir, dirs_exist_ok=True)
    
    print("Backup concluído!")

def remove_files():
    """Remove os arquivos duplicados."""
    print("Removendo arquivos duplicados...")
    
    for file_path in FILES_TO_REMOVE:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            print(f"  Removendo: {file_path}")
            os.remove(full_path)
    
    print("Remoção concluída!")

def rename_files():
    """Renomeia os arquivos consolidados para os nomes padrão."""
    print("Renomeando arquivos consolidados...")
    
    for old_path, new_path in FILES_TO_RENAME.items():
        full_old_path = BASE_DIR / old_path
        full_new_path = BASE_DIR / new_path
        
        if full_old_path.exists():
            print(f"  Renomeando: {old_path} -> {new_path}")
            
            # Remover o arquivo destino se existir
            if full_new_path.exists():
                os.remove(full_new_path)
                
            # Renomear o arquivo
            os.rename(full_old_path, full_new_path)
    
    print("Renomeação concluída!")

def main():
    print("AVISO: Este script removerá arquivos duplicados após a consolidação.")
    print("Certifique-se de que os arquivos consolidados estão funcionando corretamente.")
    
    confirmation = input("Deseja continuar? (s/n): ")
    if confirmation.lower() != 's':
        print("Operação cancelada.")
        return
    
    # Criar backup
    backup_files()
    
    # Remover arquivos duplicados
    remove_files()
    
    # Renomear arquivos consolidados
    rename_files()
    
    print()
    print("Processo concluído com sucesso!")
    print(f"Um backup foi criado em: {BACKUP_DIR}")
    print("Recomenda-se verificar se o sistema está funcionando corretamente.")

if __name__ == "__main__":
    main()
