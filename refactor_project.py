#!/usr/bin/env python
"""
Script principal para reorganização e refatoração do projeto Roar CRM.

Este script coordena a execução dos scripts de migração de código e organização
de arquivos estáticos, garantindo que sejam executados na ordem correta.
"""
import os
import sys
import subprocess
import time
from datetime import datetime

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n")
    print("=" * 80)
    print(title.center(80))
    print("=" * 80)
    print("\n")

def run_script(script_path, description):
    """Executa um script Python e retorna seu código de saída."""
    print_header(f"INICIANDO: {description}")
    
    try:
        result = subprocess.run([sys.executable, script_path], check=False)
        exit_code = result.returncode
        
        if exit_code == 0:
            print(f"\nScript concluído com sucesso: {os.path.basename(script_path)}")
        else:
            print(f"\nERRO: Script retornou código {exit_code}: {os.path.basename(script_path)}")
        
        return exit_code
    
    except Exception as e:
        print(f"\nERRO ao executar script: {str(e)}")
        return 1

def make_migrations():
    """Executa as migrações do Django após as alterações de código."""
    print_header("EXECUTANDO MIGRAÇÕES DO DJANGO")
    
    try:
        print("Gerando migrações...")
        subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
        
        print("\nAplicando migrações...")
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\nERRO ao executar migrações: {str(e)}")
        return 1
    except Exception as e:
        print(f"\nERRO inesperado: {str(e)}")
        return 1

def main():
    start_time = time.time()
    
    print_header("REORGANIZAÇÃO E REFATORAÇÃO DO PROJETO ROAR CRM")
    print(f"Data e hora de início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Confirmar com o usuário
    confirm = input("\nEsta operação irá refatorar o código e reorganizar arquivos do projeto. Deseja continuar? [s/N]: ")
    if confirm.lower() != 's':
        print("Operação cancelada pelo usuário.")
        return 0
    
    # Lista de scripts a serem executados em ordem
    scripts = [
        ("migrate_leads_app.py", "Consolidação da aplicação Leads"),
        ("organize_static_files.py", "Organização dos arquivos estáticos")
    ]
    
    # Executar cada script em sequência
    success = True
    for script_path, description in scripts:
        # Verificar se o arquivo existe
        if not os.path.exists(script_path):
            print(f"ERRO: Script não encontrado: {script_path}")
            success = False
            continue
        
        # Executar o script
        exit_code = run_script(script_path, description)
        if exit_code != 0:
            success = False
            
            # Perguntar ao usuário se deseja continuar mesmo com erro
            continue_after_error = input(f"\nO script '{script_path}' falhou. Deseja continuar com os próximos scripts? [s/N]: ")
            if continue_after_error.lower() != 's':
                print("Operação interrompida pelo usuário.")
                break
    
    # Se tudo correu bem até aqui, executar migrações
    if success:
        run_migrations = input("\nDeseja executar as migrações do Django? [S/n]: ")
        if run_migrations.lower() != 'n':
            make_migrations()
    
    # Calcular duração total
    duration = time.time() - start_time
    minutes, seconds = divmod(duration, 60)
    
    print_header("RESULTADO FINAL")
    print(f"Tempo de execução: {int(minutes)} minutos e {int(seconds)} segundos")
    
    if success:
        print("\nA reorganização e refatoração do projeto foi concluída com sucesso!")
        print("\nPróximos passos recomendados:")
        print("1. Verifique se a aplicação está funcionando corretamente")
        print("2. Atualize a documentação conforme necessário")
        print("3. Faça um commit das alterações")
    else:
        print("\nA operação foi concluída com erros. Verifique os logs acima para mais informações.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
