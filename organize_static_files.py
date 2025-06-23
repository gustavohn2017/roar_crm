"""
Script para organizar arquivos estáticos do projeto Roar CRM

Este script realiza as seguintes tarefas:
1. Identifica arquivos CSS e JS duplicados ou obsoletos
2. Organiza os arquivos em pastas lógicas dentro de static/
3. Atualiza referências nos templates se necessário
"""
import os
import shutil
import glob
import re
import filecmp
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
BACKUP_DIR = os.path.join(BASE_DIR, 'static_backup')

def backup_static():
    """Cria backup da pasta static atual."""
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    
    shutil.copytree(STATIC_DIR, BACKUP_DIR)
    print(f"Backup dos arquivos estáticos criado em: {BACKUP_DIR}")

def find_duplicate_css():
    """Identifica CSS duplicados por conteúdo."""
    css_files = glob.glob(os.path.join(STATIC_DIR, 'css', '*.css'))
    duplicate_groups = defaultdict(list)
    
    # Agrupar por tamanho primeiro (otimização)
    size_groups = defaultdict(list)
    for css_file in css_files:
        size = os.path.getsize(css_file)
        size_groups[size].append(css_file)
    
    # Comparar conteúdo apenas para arquivos do mesmo tamanho
    for size, files in size_groups.items():
        if len(files) < 2:
            continue
        
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                if filecmp.cmp(file1, file2, shallow=False):
                    file_hash = hash(open(file1, 'rb').read())
                    duplicate_groups[file_hash].append(file1)
                    duplicate_groups[file_hash].append(file2)
    
    # Remover duplicatas nas listas
    for file_hash in duplicate_groups:
        duplicate_groups[file_hash] = list(set(duplicate_groups[file_hash]))
    
    return duplicate_groups

def find_navbar_redundancies():
    """Identifica arquivos de navbar redundantes."""
    navbar_js_files = glob.glob(os.path.join(STATIC_DIR, 'js', 'navbar-*.js'))
    
    # Separar os arquivos em categorias
    categories = {
        'redesign': [],
        'minimal': [],
        'total': [],
        'other': []
    }
    
    for js_file in navbar_js_files:
        filename = os.path.basename(js_file)
        if 'redesign' in filename:
            categories['redesign'].append(js_file)
        elif 'minimal' in filename:
            categories['minimal'].append(js_file)
        elif 'total' in filename:
            categories['total'].append(js_file)
        else:
            categories['other'].append(js_file)
    
    return categories

def organize_static_files():
    """Organiza os arquivos estáticos em pastas lógicas."""
    # Criar estrutura de pastas
    folders = [
        os.path.join(STATIC_DIR, 'css', 'themes'),
        os.path.join(STATIC_DIR, 'css', 'components'),
        os.path.join(STATIC_DIR, 'js', 'components'),
        os.path.join(STATIC_DIR, 'js', 'forms'),
        os.path.join(STATIC_DIR, 'js', 'charts'),
        os.path.join(STATIC_DIR, 'js', 'nav')
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Mover arquivos para pastas apropriadas
    moves = [
        # CSS organizado por tipo
        (os.path.join(STATIC_DIR, 'css', '*theme*.css'), os.path.join(STATIC_DIR, 'css', 'themes')),
        (os.path.join(STATIC_DIR, 'css', '*responsive*.css'), os.path.join(STATIC_DIR, 'css', 'components')),
        
        # JS organizado por funcionalidade
        (os.path.join(STATIC_DIR, 'js', '*chart*.js'), os.path.join(STATIC_DIR, 'js', 'charts')),
        (os.path.join(STATIC_DIR, 'js', '*gauge*.js'), os.path.join(STATIC_DIR, 'js', 'charts')),
        (os.path.join(STATIC_DIR, 'js', '*form*.js'), os.path.join(STATIC_DIR, 'js', 'forms')),
        (os.path.join(STATIC_DIR, 'js', 'navbar-*.js'), os.path.join(STATIC_DIR, 'js', 'nav'))
    ]
    
    for pattern, dest_dir in moves:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                dest_path = os.path.join(dest_dir, filename)
                
                # Não sobrescrever se já existe (evita erro)
                if not os.path.exists(dest_path):
                    shutil.move(file_path, dest_path)
                    print(f"Movido: {file_path} → {dest_path}")

def list_redundant_files():
    """Lista arquivos redundantes que poderiam ser consolidados."""
    # Verificar duplicatas de CSS
    css_dupes = find_duplicate_css()
    if css_dupes:
        print("\nArquivos CSS com conteúdo duplicado:")
        for file_hash, files in css_dupes.items():
            print(f"  Grupo {file_hash}:")
            for file in files:
                print(f"    - {os.path.basename(file)}")
    
    # Verificar navbar JS redundantes
    navbar_files = find_navbar_redundancies()
    print("\nArquivos JS de navbar encontrados:")
    for category, files in navbar_files.items():
        print(f"  Categoria '{category}':")
        for file in files:
            print(f"    - {os.path.basename(file)}")

def generate_recommendations():
    """Gera recomendações para melhoria dos arquivos estáticos."""
    print("\n=== Recomendações para organização dos arquivos estáticos ===\n")
    
    # Recomendações para navbars
    navbar_files = find_navbar_redundancies()
    if sum(len(files) for files in navbar_files.values()) > 1:
        print("1. Consolidação de arquivos navbar:")
        print("   - Mantenha apenas o arquivo navbar mais recente/final")
        print("   - Arquivos candidatos para remoção:")
        
        # Identificar o arquivo mais recente em cada categoria
        for category, files in navbar_files.items():
            if len(files) > 1:
                # Ordenar por data de modificação (mais recente primeiro)
                files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
                
                # O primeiro é o mais recente
                print(f"     Categoria '{category}':")
                print(f"       Manter: {os.path.basename(files[0])}")
                
                for old_file in files[1:]:
                    print(f"       Remover: {os.path.basename(old_file)}")
    
    # Recomendações para CSS
    css_dupes = find_duplicate_css()
    if css_dupes:
        print("\n2. Arquivos CSS duplicados:")
        print("   Os seguintes arquivos têm conteúdo idêntico e podem ser consolidados:")
        
        for file_hash, files in css_dupes.items():
            print(f"   Grupo:")
            print(f"     Manter: {os.path.basename(files[0])}")
            
            for dupe in files[1:]:
                print(f"     Remover: {os.path.basename(dupe)}")

def main():
    print("\n=== Organizador de arquivos estáticos do Roar CRM ===\n")
    
    # Confirmar com o usuário
    confirm = input("Esta operação irá analisar e reorganizar os arquivos estáticos. Deseja continuar? [s/N]: ")
    if confirm.lower() != 's':
        print("Operação cancelada pelo usuário.")
        return
    
    try:
        # Criar backup
        backup_static()
        
        # Executar organização
        organize_static_files()
        
        # Listar redundâncias
        list_redundant_files()
        
        # Gerar recomendações
        generate_recommendations()
        
        print("\n=== Operação concluída ===")
        print("Os arquivos estáticos foram reorganizados em uma estrutura mais lógica.")
        print("Um backup dos arquivos originais foi criado em:", BACKUP_DIR)
        
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro durante a operação: {str(e)}")
        print("A operação foi interrompida.")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
