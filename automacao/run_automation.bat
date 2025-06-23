@echo off
echo Executando automação do Lions CRM...

REM Caminho para o interpretador Python e o arquivo manage.py
set PYTHON="c:\lions_crm\venv\Scripts\python.exe"
set MANAGE="c:\lions_crm\roar\manage.py"

REM Executa o comando de automação
%PYTHON% %MANAGE% processar_automacao

echo Automação concluída às %time%
