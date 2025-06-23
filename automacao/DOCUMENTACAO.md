# Lions CRM - Documentação do Sistema de Automação

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Componentes Principais](#3-componentes-principais)
   - [3.1 Lead Scoring](#31-lead-scoring)
   - [3.2 Workflows Automáticos](#32-workflows-automáticos)
   - [3.3 Campanhas de Nutrição](#33-campanhas-de-nutrição)
   - [3.4 Gatilhos Automáticos](#34-gatilhos-automáticos)
4. [Serviços de Negócios](#4-serviços-de-negócios)
5. [Interfaces do Sistema](#5-interfaces-do-sistema)
6. [Configuração e Implantação](#6-configuração-e-implantação)
7. [Monitoramento e Manutenção](#7-monitoramento-e-manutenção)
8. [FAQ](#8-faq)

## 1. Visão Geral

O sistema de automação do Lions CRM é uma solução abrangente para automação de marketing e vendas que permite a execução automática de tarefas repetitivas, pontuação inteligente de leads, campanhas de nutrição programadas e gatilhos baseados em comportamento do usuário.

### Objetivos Principais:

- **Qualificação Automatizada de Leads**: Classificação automática baseada em critérios configuráveis
- **Eficiência de Processos**: Automação de tarefas repetitivas para liberar tempo da equipe 
- **Comunicação Consistente**: Entrega programada de comunicações personalizadas
- **Priorização de Leads**: Foco da equipe de vendas nos leads mais promissores
- **Rastreamento de Interações**: Histórico completo de todas as automações executadas

## 2. Arquitetura do Sistema

O sistema de automação está organizado como um módulo Django independente (`automacao`) que se integra ao núcleo do Lions CRM. A arquitetura segue o padrão Model-View-Template (MVT) do Django com as seguintes camadas adicionais:

### Camadas do Sistema

1. **Modelos de Dados**: Definições em `models.py` para estruturas de dados
2. **Camada de Serviço**: Implementação de lógica de negócios em `services.py`
3. **Camada de Apresentação**: Views e templates para interação com usuário
4. **Camada de Integração**: Signals e APIs para integração com outros módulos
5. **Camada de Infraestrutura**: Agendador de tarefas para execuções programadas

### Dependências

- **Core do CRM**: Integração com módulos de leads e vendedores
- **Django ORM**: Persistência de dados
- **Django Template Engine**: Renderização de interfaces
- **Sistema Operacional**: Agendador de tarefas (Windows Task Scheduler / Linux Cron)

## 3. Componentes Principais

### 3.1 Lead Scoring

O sistema de pontuação de leads (Lead Scoring) utiliza critérios configuráveis para atribuir pontuações a cada lead, permitindo a classificação automática baseada em seu potencial de conversão.

#### Modelos Principais:
- **LeadScore**: Armazena a pontuação total e por categoria para cada lead
- **CriterioScore**: Define critérios específicos para pontuação

#### Categorias de Pontuação:

1. **Demográfica** (0-40 pontos): Baseada em características do perfil do lead
   - Cargo (0-20 pontos)
   - Tamanho da empresa (0-10 pontos)
   - Localização (0-5 pontos)
   - Setor de atuação (0-5 pontos)

2. **Comportamental** (0-30 pontos): Baseada em ações do lead
   - Visitas a páginas específicas (0-15 pontos)
   - Downloads de materiais (0-10 pontos)
   - Tempo no site (0-5 pontos)

3. **Engajamento** (0-15 pontos): Baseada na interação com comunicações
   - Abertura de emails (0-5 pontos)
   - Cliques em links (0-5 pontos)
   - Resposta a comunicações (0-5 pontos)

4. **Interesse** (0-15 pontos): Baseada em interesse específico em produtos
   - Visualização de páginas de produtos (0-5 pontos)
   - Visualização de preços (0-5 pontos)
   - Solicitação de demonstração (0-5 pontos)

#### Classificações:

- **Frio (0-30 pontos)**: Lead com baixa probabilidade de conversão
- **Morno (31-60 pontos)**: Lead com potencial médio de conversão
- **Quente (61-80 pontos)**: Lead com alto potencial de conversão
- **Muito Quente (81-100 pontos)**: Lead pronto para conversão

### 3.2 Workflows Automáticos

Workflows são sequências de ações automatizadas que podem ser executadas em resposta a eventos específicos no sistema.

#### Modelos Principais:
- **Workflow**: Define o fluxo de trabalho completo
- **AcaoWorkflow**: Define ações individuais dentro do workflow
- **ExecucaoWorkflow**: Rastreia a execução de workflows para leads específicos

#### Gatilhos de Workflow:

- **Lead Criado**: Executa quando um novo lead é registrado
- **Status Alterado**: Executa quando o status de um lead muda
- **Sem Contato**: Executa quando não há contato com o lead por X dias
- **Score Alterado**: Executa quando o score de um lead atinge determinado valor
- **Data Específica**: Executa em uma data programada
- **Ação Manual**: Executa por acionamento manual de um usuário

#### Tipos de Ações:

- **Enviar E-mail**: Envia uma mensagem para o lead
- **Enviar WhatsApp**: Envia uma mensagem via WhatsApp
- **Criar Tarefa**: Cria uma tarefa para um vendedor
- **Alterar Status**: Muda o status do lead
- **Atribuir Vendedor**: Atribui o lead a um vendedor específico
- **Aguardar**: Pausa o workflow por um período
- **Notificar Usuário**: Envia uma notificação para um usuário do sistema

### 3.3 Campanhas de Nutrição

Campanhas de nutrição são sequências programadas de comunicações e ações para educar e engajar leads ao longo do tempo.

#### Modelos Principais:
- **CampanhaNutricao**: Define a campanha completa
- **EtapaCampanha**: Define etapas individuais da campanha
- **ParticipacaoCampanha**: Rastreia a participação do lead em uma campanha

#### Tipos de Campanhas:

- **Boas-vindas**: Orientação inicial para novos leads
- **Educacional**: Fornecimento de conteúdo informativo
- **Reengajamento**: Ativação de leads inativos
- **Produto Específico**: Focada em um produto ou serviço
- **Sazonal**: Relacionada a eventos ou épocas específicas

#### Tipos de Etapas:

- **E-mail**: Envio de mensagem por email
- **WhatsApp**: Envio de mensagem via WhatsApp
- **Tarefa**: Criação de tarefa para vendedor
- **Aguardar**: Período de espera entre etapas

### 3.4 Gatilhos Automáticos

Gatilhos automáticos monitoram eventos específicos no sistema e iniciam ações quando esses eventos ocorrem.

#### Modelo Principal:
- **GatilhoAutomatico**: Define eventos e condições para acionar workflows

#### Tipos de Eventos:

- **Lead Criado**: Quando um novo lead é registrado
- **Contato Realizado**: Quando há um contato com o lead
- **Status Alterado**: Quando o status do lead muda
- **Sem Atividade**: Quando não há atividade do lead por X dias
- **Score Threshold**: Quando o score atinge determinado valor
- **Data Vencimento**: Quando uma data específica é atingida
- **E-mail Aberto**: Quando o lead abre um email
- **Link Clicado**: Quando o lead clica em um link

## 4. Serviços de Negócios

Os serviços de negócios encapsulam a lógica de execução de funcionalidades do sistema:

### LeadScoringService

Responsável pela pontuação automática de leads:
- `calcular_score_lead()`: Calcula pontuação para um lead específico
- `recalcular_todos_scores()`: Recalcula pontuações para todos os leads
- `aplicar_criterio()`: Aplica um critério específico a um lead

### WorkflowService

Gerencia a execução de workflows:
- `executar_workflow()`: Inicia a execução de um workflow para um lead
- `continuar_workflow()`: Continua a execução de um workflow pausado
- `cancelar_workflow()`: Cancela a execução de um workflow
- `lead_atende_criterios()`: Verifica se um lead atende aos critérios do workflow

### CampanhaService

Coordena campanhas de nutrição:
- `processar_entradas_campanhas()`: Verifica leads que devem entrar em campanhas
- `executar_proxima_etapa()`: Executa a próxima etapa para um lead em campanha
- `cancelar_participacao()`: Remove um lead de uma campanha
- `lead_atende_criterios_campanha()`: Verifica se lead atende aos critérios da campanha

### GatilhoService

Monitora e processa gatilhos automáticos:
- `verificar_gatilhos()`: Verifica gatilhos que devem ser acionados
- `processar_evento()`: Processa um evento específico
- `registrar_evento()`: Registra a ocorrência de um evento no sistema

## 5. Interfaces do Sistema

### Interface Administrativa

Acessível via Django Admin em `/admin/automacao/`:
- Gerenciamento completo de todos os modelos
- Configuração detalhada de parâmetros
- Visualização de execuções e histórico

### Interface do Usuário

Acessível via módulo de automação em `/automacao/`:
- **Dashboard**: Visão geral e estatísticas (/automacao/)
- **Lead Scoring**: Visualização e gestão de scores (/automacao/lead-scoring/)
- **Workflows**: Gestão de workflows (/automacao/workflows/)
- **Campanhas**: Gestão de campanhas (/automacao/campanhas/)
- **Histórico**: Registro de automações executadas (/automacao/historico/)

### APIs para Integração

- `/automacao/api/score-lead/<id>/`: API para pontuação de lead específico
- `/automacao/api/executar-workflow/<id>/`: API para execução manual de workflow
- `/automacao/api/adicionar-leads-campanha/<id>/`: API para adicionar leads a campanhas

## 6. Configuração e Implantação

### Requisitos do Sistema

- Django 3.2+
- Python 3.8+
- Banco de dados SQL (SQLite, PostgreSQL, MySQL)
- Agendador de tarefas do sistema operacional

### Processo de Instalação

1. Garantir que o módulo `automacao` está listado em `INSTALLED_APPS` no `settings.py`
2. Executar migrações do banco de dados:
   ```
   python manage.py migrate automacao
   ```
3. Configurar o agendador de tarefas conforme instruções em `AGENDAMENTO.md`
4. Verificar direitos de acesso para execução de comandos agendados

### Configuração do Agendador de Tarefas

Consulte o arquivo `AGENDAMENTO.md` para instruções detalhadas sobre:
- Configuração no Windows Task Scheduler
- Configuração em sistemas Linux com Cron
- Parâmetros de execução recomendados

## 7. Monitoramento e Manutenção

### Logs do Sistema

Logs são armazenados em:
- `/logs/roar.log`: Log principal do sistema
- `/logs/automacao.log`: Log específico das execuções agendadas

### Monitoramento de Desempenho

Métricas chave a serem monitoradas:
- Tempo médio de execução de workflows
- Taxa de sucesso de automações
- Número de leads processados por período
- Uso de recursos do sistema durante execuções agendadas

### Backup de Dados

Recomendado backup diário das seguintes tabelas:
- `automacao_leadscore`
- `automacao_execucaoworkflow`
- `automacao_participacaocampanha`
- `automacao_historicoautomacao`

## 8. FAQ

### Perguntas Frequentes

**P: Como criar um novo workflow?**  
R: Acesse `/automacao/workflows/create/` e preencha o formulário com nome, descrição, gatilho e condições. Em seguida, adicione as ações desejadas.

**P: Como recalcular o score de todos os leads?**  
R: Acesse `/automacao/lead-scoring/recalcular/` ou use o botão "Recalcular Scores" no dashboard de Lead Scoring.

**P: Como pausar uma campanha de nutrição?**  
R: Na lista de campanhas, use o toggle de status para mudar o status da campanha para "Pausada".

**P: O que acontece se um lead for removido?**  
R: Todas as associações de automação (scores, execuções, participações) são removidas em cascata.

**P: Como verificar se o agendador está funcionando?**  
R: Verifique o arquivo de log em `/logs/automacao.log` para confirmar as execuções programadas.

**P: Como executar a automação manualmente?**  
R: Use o botão "Executar Automação" no dashboard ou execute o comando:
```
python manage.py processar_automacao
```

---

© 2025 Lions CRM - Sistema de Automação de Marketing e Vendas
