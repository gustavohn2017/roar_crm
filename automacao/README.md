# Lions CRM - Sistema de Automação de Marketing e Vendas

## Visão Geral

O módulo de automação do Lions CRM fornece uma solução completa para automatização de tarefas relacionadas ao processo de vendas e nutrição de leads. Com este sistema, é possível configurar fluxos de trabalho personalizados, pontuação automática de leads, campanhas de nutrição e gatilhos baseados em eventos.

## Principais Funcionalidades

### 1. Pontuação de Leads (Lead Scoring)

Sistema avançado de pontuação de leads baseado em 4 categorias principais:
- **Demográficos**: Pontuação baseada em dados como localização, tamanho da empresa, cargo, etc.
- **Comportamentais**: Pontuação baseada em ações do lead no site, interações com conteúdo, etc.
- **Engajamento**: Pontuação baseada em respostas a e-mails, participação em eventos, etc.
- **Interesse**: Pontuação baseada em interesse demonstrado em produtos específicos, visitas a páginas de preço, etc.

O sistema calcula automaticamente um score total e classifica os leads em categorias (Frio, Morno, Quente, Muito Quente).

### 2. Automação de Workflows

Os workflows permitem criar sequências automatizadas de ações que são executadas quando determinados eventos ocorrem:
- Criação de novos leads
- Mudança de status
- Atualização de score
- Períodos sem contato
- Datas específicas
- Ações manuais

Cada workflow pode conter múltiplas ações como envio de e-mails, criação de tarefas, mudança de status, notificações, etc.

### 3. Campanhas de Nutrição

Campanhas sequenciais para educar e nutrir leads ao longo do tempo:
- Sequências de e-mails programados
- Conteúdo personalizado
- Critérios de entrada e saída configuráveis
- Acompanhamento de progresso e engajamento

### 4. Gatilhos Automáticos

Sistema de gatilhos que monitora eventos específicos e inicia ações automatizadas:
- E-mails abertos/links clicados
- Formulários preenchidos
- Páginas específicas visitadas
- Critérios de pontuação atingidos

## Componentes Técnicos

### Modelos de Dados
- `LeadScore`: Armazena e gerencia pontuação de leads
- `CriterioScore`: Define critérios para pontuação
- `Workflow`: Define fluxos de trabalho automatizados
- `AcaoWorkflow`: Ações individuais dentro de um workflow
- `CampanhaNutricao`: Define campanhas de nutrição
- `EtapaCampanha`: Etapas individuais de uma campanha
- `ExecucaoWorkflow`: Registra execuções de workflows
- `ParticipacaoCampanha`: Registra participação de leads em campanhas
- `GatilhoAutomatico`: Define gatilhos baseados em eventos
- `HistoricoAutomacao`: Mantém histórico de todas as ações do sistema

### Serviços
- `LeadScoringService`: Responsável pela pontuação automática de leads
- `WorkflowService`: Gerencia execução de workflows
- `CampanhaService`: Coordena campanhas de nutrição
- `GatilhoService`: Monitora e processa gatilhos

## Executando a Automação

O sistema inclui um comando de gerenciamento para processar automaticamente workflows, campanhas e gatilhos programados:

```bash
python manage.py processar_automacao
```

Para configurar a execução automática periódica, consulte o arquivo `AGENDAMENTO.md`.

## Dashboard e Relatórios

O módulo inclui dashboards e relatórios completos para monitorar:
- Distribuição de scores de leads
- Performance de campanhas
- Estatísticas de execução de workflows
- Histórico de automação

## Integrações

O sistema de automação se integra com:
- Sistema de e-mail marketing
- Notificações por WhatsApp
- Calendário para agendamento de tarefas
- Sistema de atribuição de leads para vendedores
