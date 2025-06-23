#!/usr/bin/env python
"""
Script para resolver conflitos de modelos durante o processo de refatoração.
Este script desativa temporariamente os arquivos duplicados de modelos
para evitar conflitos de registro de modelos no Django.

Uso:
    python resolve_model_conflicts.py
"""

import os
import shutil
import sys
from pathlib import Path

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_DIR = os.path.join(BASE_DIR, 'leads')
BACKUP_DIR = os.path.join(BASE_DIR, 'temp_backup')

# Arquivos que podem causar conflitos
CONFLICT_FILES = [
    'models_comunicacao.py',
    'forms_comunicacao.py',
    'views_comunicacao.py'
]

def create_backup_dir():
    """Cria diretório de backup se não existir."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Diretório de backup criado: {BACKUP_DIR}")

def disable_conflict_files():
    """Desativa temporariamente os arquivos que causam conflitos."""
    create_backup_dir()
    
    for filename in CONFLICT_FILES:
        src_path = os.path.join(LEADS_DIR, filename)
        if os.path.exists(src_path):
            # Criar backup
            backup_path = os.path.join(BACKUP_DIR, filename)
            shutil.copy2(src_path, backup_path)
            
            # Renomear arquivo original
            disable_path = f"{src_path}.disabled"
            os.rename(src_path, disable_path)
            print(f"Arquivo desativado: {filename} -> {filename}.disabled")
        else:
            print(f"Arquivo não encontrado: {filename}")

def restore_conflict_files():
    """Restaura arquivos conflitantes do backup."""
    for filename in CONFLICT_FILES:
        backup_path = os.path.join(BACKUP_DIR, filename)
        disabled_path = os.path.join(LEADS_DIR, f"{filename}.disabled")
        dest_path = os.path.join(LEADS_DIR, filename)
        
        if os.path.exists(backup_path) and os.path.exists(disabled_path):
            os.replace(disabled_path, dest_path)
            print(f"Arquivo restaurado: {filename}")
        elif os.path.exists(disabled_path):
            os.rename(disabled_path, dest_path)
            print(f"Arquivo renomeado: {filename}.disabled -> {filename}")

def update_admin_file():
    """Atualiza o arquivo admin.py para usar os modelos consolidados."""
    admin_path = os.path.join(LEADS_DIR, 'admin.py')
    admin_new_path = os.path.join(LEADS_DIR, 'admin_new.py')
    admin_backup_path = os.path.join(BACKUP_DIR, 'admin.py')
    
    if os.path.exists(admin_path) and os.path.exists(admin_new_path):
        # Fazer backup do arquivo admin original
        shutil.copy2(admin_path, admin_backup_path)
        
        # Substituir com o novo arquivo admin
        shutil.copy2(admin_new_path, admin_path)
        print("Arquivo admin.py atualizado com sucesso!")
    else:
        print("Erro: não foi possível atualizar admin.py. Arquivos não encontrados.")

def main():
    print("\n=== Resolver Conflitos de Modelos ===\n")
    
    # Confirmar com o usuário
    action = input("O que você deseja fazer?\n"
                   "1 - Desativar arquivos conflitantes\n"
                   "2 - Restaurar arquivos desativados\n"
                   "3 - Atualizar apenas arquivo admin.py\n"
                   "Escolha (1/2/3): ")
    
    if action == "1":
        disable_conflict_files()
        update_admin_file()
        print("\nArquivos conflitantes foram desativados e admin.py atualizado.")
        print("Agora você pode executar o servidor Django sem conflitos de modelos.")
        print("\nPara restaurar os arquivos posteriormente, execute:")
        print("python resolve_model_conflicts.py e escolha a opção 2")
    
    elif action == "2":
        restore_conflict_files()
        print("\nArquivos restaurados. Observe que isso pode causar conflitos de modelos novamente.")
    
    elif action == "3":
        update_admin_file()
        print("\nApenas o arquivo admin.py foi atualizado para usar os modelos consolidados.")
    
    else:
        print("\nEscolha inválida. Nenhuma alteração foi feita.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
