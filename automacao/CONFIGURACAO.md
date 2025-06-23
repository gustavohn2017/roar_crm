# Guia de Configuração do Sistema de Automação

Este documento fornece instruções passo a passo para configurar o sistema de automação do Lions CRM.

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Configuração Inicial](#2-configuração-inicial)
3. [Configuração do Lead Scoring](#3-configuração-do-lead-scoring)
4. [Configuração dos Workflows](#4-configuração-dos-workflows)
5. [Configuração de Campanhas de Nutrição](#5-configuração-de-campanhas-de-nutrição)
6. [Configuração dos Gatilhos Automáticos](#6-configuração-dos-gatilhos-automáticos)
7. [Agendamento de Tarefas](#7-agendamento-de-tarefas)
8. [Resolução de Problemas](#8-resolução-de-problemas)

## 1. Pré-requisitos

- Lions CRM instalado e configurado
- Acesso de administrador ao sistema
- Python 3.8 ou superior
- Permissão para executar agendador de tarefas do sistema operacional

## 2. Configuração Inicial

### Verificação da Instalação

1. Acesse o sistema e verifique se o módulo de automação está visível no menu
2. Acesse `/automacao/` para verificar se o dashboard está funcionando
3. Verifique se as tabelas do banco de dados foram criadas:
   ```powershell
   cd c:\lions_crm\roar
   python manage.py dbshell
   .tables
   ```
   Você deve ver tabelas como `automacao_leadscore`, `automacao_workflow`, etc.

### Configuração de Permissões

1. Acesse o Admin do Django em `/admin/`
2. Vá para "Grupos" e crie ou edite grupos para permissões:
   - `Administradores`: Acesso completo ao sistema de automação
   - `Supervisores`: Pode configurar e monitorar automação
   - `Vendedores`: Apenas visualizar resultados da automação

## 3. Configuração do Lead Scoring

### Criação de Critérios de Score

1. Acesse o Admin em `/admin/automacao/criterioscore/`
2. Clique em "Adicionar Critério de Score"
3. Preencha:
   - **Nome**: Nome descritivo (ex: "Cargo de Decisão")
   - **Tipo**: Selecione o tipo (Demográfico, Comportamental, etc.)
   - **Pontos**: Valor numérico (1-50)
   - **Condição**: JSON com critérios (ex: `{"campo": "cargo", "valores": ["CEO", "Diretor"]}`)
   - **Ativo**: Marque para ativar o critério

### Exemplos de Critérios

#### Critério Demográfico:
```json
{
  "campo": "cargo",
  "valores": ["CEO", "Diretor", "Gerente"],
  "operador": "in"
}
```

#### Critério Comportamental:
```json
{
  "evento": "visita_pagina",
  "pagina": "precos",
  "min_visitas": 2
}
```

#### Critério de Engajamento:
```json
{
  "evento": "abriu_email",
  "min_aberturas": 3
}
```

### Recalculando Scores

Após criar critérios, recalcule os scores:
1. Acesse `/automacao/lead-scoring/recalcular/`
2. Ou use o botão "Recalcular Scores" no dashboard

## 4. Configuração dos Workflows

### Criação de um Workflow

1. Acesse `/automacao/workflows/create/`
2. Preencha:
   - **Nome**: Nome descritivo do workflow
   - **Descrição**: Descrição detalhada
   - **Trigger**: Evento que dispara o workflow
   - **Condições**: JSON com condições específicas
   - **Ativo**: Ativar/desativar workflow

### Adicionando Ações ao Workflow

1. Na página de detalhe do workflow, clique em "Adicionar Ação"
2. Preencha:
   - **Ordem**: Ordem de execução (1, 2, 3, etc.)
   - **Tipo de Ação**: Selecione o tipo (enviar email, criar tarefa, etc.)
   - **Parâmetros**: JSON com parâmetros específicos da ação
   - **Delay em Dias**: Dias para aguardar antes da execução

### Exemplos de Parâmetros de Ações

#### Enviar Email:
```json
{
  "assunto": "Proposta comercial para {{lead.nome}}",
  "corpo": "Prezado(a) {{lead.nome}},\n\nSegue nossa proposta...",
  "usar_template": true,
  "template_id": 5
}
```

#### Criar Tarefa:
```json
{
  "titulo": "Ligar para {{lead.nome}}",
  "descricao": "Lead qualificado, fazer contato.",
  "prioridade": "alta",
  "atribuir_para": "vendedor_atual"
}
```

## 5. Configuração de Campanhas de Nutrição

### Criação de uma Campanha

1. Acesse `/automacao/campanhas/create/`
2. Preencha:
   - **Nome**: Nome da campanha
   - **Descrição**: Descrição detalhada
   - **Status**: Rascunho, Ativa, Pausada, etc.
   - **Data Início**: Data para iniciar a campanha
   - **Critérios de Segmentação**: JSON com critérios para selecionar leads

### Adicionando Etapas à Campanha

1. Na página de detalhe da campanha, clique em "Adicionar Etapa"
2. Preencha:
   - **Ordem**: Ordem de execução (1, 2, 3, etc.)
   - **Nome**: Nome descritivo da etapa
   - **Tipo**: Email, WhatsApp, Tarefa, etc.
   - **Delay em Dias**: Dias após a etapa anterior
   - **Conteúdo**: Conteúdo específico da etapa

### Exemplo de Critérios de Segmentação

```json
{
  "status": ["novo", "qualificando"],
  "score_minimo": 30,
  "sem_campanhas_ativas": true
}
```

## 6. Configuração dos Gatilhos Automáticos

### Criação de um Gatilho

1. Acesse o Admin em `/admin/automacao/gatilhoautomatico/`
2. Clique em "Adicionar Gatilho Automático"
3. Preencha:
   - **Nome**: Nome descritivo
   - **Evento**: Tipo de evento que ativa o gatilho
   - **Condições**: JSON com condições específicas
   - **Workflow**: Workflow a ser executado
   - **Ativo**: Ativar/desativar gatilho

### Exemplo de Condições de Gatilho

```json
{
  "score_minimo": 70,
  "dias_sem_contato": 5,
  "status_excluidos": ["convertido", "perdido"]
}
```

## 7. Agendamento de Tarefas

Para garantir que automações sejam executadas regularmente, configure o agendador de tarefas:

### No Windows (Task Scheduler)

Para maiores detalhes, consulte o arquivo `AGENDAMENTO.md`.

Executando manualmente:
```powershell
cd c:\lions_crm\roar
powershell -ExecutionPolicy Bypass -File "automacao\run_automation.ps1"
```

## 8. Resolução de Problemas

### Verificando Logs

Os logs de automação são armazenados em:
```
c:\lions_crm\roar\logs\automacao.log
```

### Problemas Comuns

1. **Workflows não executam**:
   - Verifique se o workflow está ativo
   - Verifique se as condições estão sendo atendidas
   - Verifique se o agendador está configurado corretamente

2. **Scores não calculados**:
   - Verifique se existem critérios ativos
   - Execute manualmente a recalculação de scores

3. **Campanhas não estão enviando emails**:
   - Verifique a configuração de email no settings.py
   - Verifique se a campanha está ativa
   - Verifique se os templates de email existem

Para mais informações, consulte a documentação completa em `DOCUMENTACAO.md`.

---

© 2025 Lions CRM
