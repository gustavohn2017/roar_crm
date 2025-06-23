# Configuração do Agendamento para Automação do Lions CRM

Este arquivo contém instruções para configurar o agendamento da automação do sistema Lions CRM.

## Configuração no Windows (Task Scheduler)

1. Abra o Task Scheduler (Agendador de Tarefas) do Windows
2. Clique em "Create Task" (Criar Tarefa)
3. Na guia "General" (Geral):
   - Dê um nome como "Lions CRM - Automação"
   - Adicione uma descrição
   - Selecione "Run whether user is logged on or not" (Executar independentemente do usuário estar logado)
   - Marque "Run with highest privileges" (Executar com privilégios elevados)

4. Na guia "Triggers" (Gatilhos), clique em "New" (Novo):
   - Begin the task: "On a schedule" (Em um agendamento)
   - Settings: Daily (Diariamente)
   - Recur every: 1 day (1 dia)
   - Start time: Configurar horário desejado
   - Marcar "Repeat task every" (Repetir tarefa a cada): 15 minutes (15 minutos)
   - Duration: Indefinitely (Indefinidamente)
   - Enabled: Yes (Sim)

5. Na guia "Actions" (Ações), clique em "New" (Novo):
   - Action: "Start a program" (Iniciar um programa)
   - Program/script: `powershell.exe`
   - Add arguments (optional): `-ExecutionPolicy Bypass -File "c:\lions_crm\roar\automacao\run_automation.ps1"`
   - Start in: `c:\lions_crm\roar`

6. Na guia "Conditions" (Condições):
   - Desmarque "Start the task only if the computer is on AC power" (Iniciar somente se o computador estiver conectado à tomada)

7. Na guia "Settings" (Configurações):
   - "If the task fails, restart every": 5 minutes (5 minutos)
   - "Attempt to restart up to": 3 times (3 vezes)
   - "If the task is already running, then the following rule applies": "Do not start a new instance" (Não iniciar nova instância)

8. Clique em OK e forneça as credenciais de administrador quando solicitado

## Configuração no Linux (Cron)

Se estiver usando um servidor Linux, configure o cron da seguinte forma:

1. Abra o editor de crontab:
   ```
   crontab -e
   ```

2. Adicione a linha para executar a cada 15 minutos:
   ```
   */15 * * * * cd /caminho/para/lions_crm/roar && /caminho/para/venv/bin/python manage.py processar_automacao >> /var/log/lions_crm/automacao.log 2>&1
   ```

3. Salve e feche o editor

## Logs

Os logs da automação são salvos em:

- Windows: `c:\lions_crm\roar\logs\roar.log`
- Linux: `/var/log/lions_crm/automacao.log` (se configurado como acima)

## Execução Manual

Para executar a automação manualmente a qualquer momento:

```
python manage.py processar_automacao
```

Para forçar a execução de todos os workflows e campanhas, independente de condições de tempo:

```
python manage.py processar_automacao --force
```
