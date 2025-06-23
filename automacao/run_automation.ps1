# PowerShell script para automação do Lions CRM
Write-Host "Iniciando processamento de automação do Lions CRM..." -ForegroundColor Green

# Definir caminhos
$PYTHON = "c:\lions_crm\venv\Scripts\python.exe"
$MANAGE = "c:\lions_crm\roar\manage.py"
$LOGFILE = "c:\lions_crm\roar\logs\automacao.log"

# Criar diretório de logs se não existir
if (-not (Test-Path "c:\lions_crm\roar\logs")) {
    New-Item -ItemType Directory -Path "c:\lions_crm\roar\logs" | Out-Null
}

# Escrever cabeçalho no log
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $LOGFILE -Value "==========================================`r`n"
Add-Content -Path $LOGFILE -Value "Execução automática iniciada em: $timestamp`r`n"

try {
    # Mudar para o diretório do projeto
    Set-Location -Path "c:\lions_crm\roar"
    
    # Executar o comando de automação e capturar a saída
    $output = & $PYTHON $MANAGE processar_automacao 2>&1
    
    # Registrar saída no log
    Add-Content -Path $LOGFILE -Value $output
    
    # Exibir saída no console
    $output
    
    Write-Host "Automação concluída com sucesso!" -ForegroundColor Green
    Add-Content -Path $LOGFILE -Value "`r`nExecução concluída com sucesso em: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`r`n"
}
catch {
    $errorMsg = $_.Exception.Message
    Write-Host "Erro na execução da automação: $errorMsg" -ForegroundColor Red
    
    # Registrar erro no log
    Add-Content -Path $LOGFILE -Value "`r`nERRO: $errorMsg`r`n"
    Add-Content -Path $LOGFILE -Value $_.Exception.StackTrace
}

# Linha divisória no log para facilitar leitura
Add-Content -Path $LOGFILE -Value "==========================================`r`n"
