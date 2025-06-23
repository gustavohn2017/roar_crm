#!/usr/bin/env python
"""
Script para migrar o código da aplicação leads para usar os novos modelos e formulários consolidados.
"""
import os
import sys
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_DIR = os.path.join(BASE_DIR, 'leads')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups', f'leads_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

def backup_files():
    """Cria backup dos arquivos originais."""
    print("Criando backup dos arquivos originais...")
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)    # Arquivos a serem backupeados
    files_to_backup = [
        'models.py',
        'models_comunicacao.py',
        'forms.py',
        'forms_comunicacao.py',
        'views.py',
        'views_comunicacao.py',
        'urls.py',
        'admin.py'
    ]
    
    for file in files_to_backup:
        src = os.path.join(LEADS_DIR, file)
        if os.path.exists(src):
            dst = os.path.join(BACKUP_DIR, file)
            shutil.copy2(src, dst)
            print(f"  - Backup de {file} criado")
    
    print("Backup concluído.")

def migrate_files():
    """Substitui os arquivos antigos pelos novos consolidados."""
    print("Migrando arquivos...")    # Mapeamento de arquivos
    files_map = {
        'models_new.py': 'models.py',
        'forms_new.py': 'forms.py',
        'views_new.py': 'views.py',
        'urls_new.py': 'urls.py',
        'admin_new.py': 'admin.py',
    }
    
    for src_name, dst_name in files_map.items():
        src = os.path.join(LEADS_DIR, src_name)
        dst = os.path.join(LEADS_DIR, dst_name)
        
        if os.path.exists(src):
            # Sobrescreve o arquivo de destino
            shutil.copy2(src, dst)
            print(f"  - {src_name} migrado para {dst_name}")
        else:
            print(f"  [ERRO] Arquivo {src_name} não encontrado")
    
    print("Migração de arquivos concluída.")

def remove_deprecated_files():
    """Remove arquivos obsoletos após a consolidação."""
    print("Removendo arquivos obsoletos...")    # Arquivos a serem removidos
    files_to_remove = [
        'models_comunicacao.py',
        'forms_comunicacao.py',
        'views_comunicacao.py',
        'models_new.py',
        'forms_new.py',
        'views_new.py',
        'urls_new.py',
        'admin_new.py'
    ]
    
    for file in files_to_remove:
        path = os.path.join(LEADS_DIR, file)
        if os.path.exists(path):
            os.remove(path)
            print(f"  - {file} removido")
    
    print("Remoção de arquivos obsoletos concluída.")

def main():
    print("\n=== Iniciando migração para modelos consolidados ===\n")
    
    # Confirmar com o usuário
    confirm = input("Esta operação irá consolidar os arquivos de modelo, formulário e views da aplicação leads. Deseja continuar? [s/N]: ")
    if confirm.lower() != 's':
        print("Migração cancelada pelo usuário.")
        return
    
    try:
        # Executar os passos da migração
        backup_files()
        migrate_files()
        remove_deprecated_files()
        
        print("\n=== Migração concluída com sucesso! ===")
        print("\nOs modelos, formulários e views da aplicação leads foram consolidados.")
        print("Um backup dos arquivos originais foi criado em:", BACKUP_DIR)
        print("\nVerifique se tudo está funcionando corretamente e execute as migrações do Django se necessário:")
        print("  python manage.py makemigrations leads")
        print("  python manage.py migrate leads")
        
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro durante a migração: {str(e)}")
        print("A migração foi interrompida. Verifique os arquivos e tente novamente.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
