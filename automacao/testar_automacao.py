# Script de teste para o módulo de automação
# Este script cria alguns dados de teste e verifica se o sistema de automação está funcionando corretamente

import os
import sys
import django
import traceback
from datetime import timedelta
from django.utils import timezone

# Configurar ambiente Django
sys.path.append('c:/lions_crm/roar')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roar_crm.settings')
django.setup()

# Importar modelos
from django.contrib.auth.models import User
from leads.models import Lead
from automacao.models import (
    Workflow, AcaoWorkflow, LeadScore, CriterioScore, 
    CampanhaNutricao, EtapaCampanha, GatilhoAutomatico
)
from automacao.services import LeadScoringService, WorkflowService, CampanhaService

# Funções de teste
def criar_workflow_teste():
    """Cria um workflow de teste para leads sem contato há mais de 3 dias"""
    try:
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            print("ERRO: Nenhum usuário admin encontrado")
            return

        # Criar workflow
        workflow = Workflow.objects.create(
            nome="Workflow de Teste - Sem Contato",
            descricao="Workflow para leads sem contato há mais de 3 dias",
            trigger="sem_contato",
            condicoes='{"dias_sem_contato": 3}',
            ativo=True,
            criado_por=admin
        )
        print(f"Workflow criado: {workflow.nome}")

        # Criar ações para o workflow
        AcaoWorkflow.objects.create(
            workflow=workflow,
            ordem=1,
            tipo_acao="enviar_email",
            parametros='{"assunto": "Sentimos sua falta!", "corpo": "Olá {{lead.nome}},\\n\\nNotamos que faz um tempo desde nosso último contato. Podemos ajudar em algo?\\n\\nAtt,\\nEquipe Lions CRM"}',
            delay_dias=0
        )
        
        AcaoWorkflow.objects.create(
            workflow=workflow,
            ordem=2,
            tipo_acao="criar_tarefa",
            parametros='{"titulo": "Ligar para {{lead.nome}}", "descricao": "Lead sem contato há mais de 3 dias", "prioridade": "alta"}',
            delay_dias=2
        )
        
        print("Ações do workflow criadas com sucesso")
        return workflow
    except Exception as e:
        print(f"ERRO ao criar workflow: {str(e)}")
        return None

def criar_campanha_teste():
    """Cria uma campanha de nutrição de teste"""
    try:
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            print("ERRO: Nenhum usuário admin encontrado")
            return

        # Criar campanha
        campanha = CampanhaNutricao.objects.create(
            nome="Campanha de Boas-vindas",
            descricao="Sequência de boas-vindas para novos leads",
            objetivo="Apresentar a empresa e produtos",
            status="ativa",
            data_inicio=timezone.now(),
            criado_por=admin,
            criterios_segmentacao='{"status": ["novo", "qualificando"]}'
        )
        print(f"Campanha criada: {campanha.nome}")

        # Criar etapas da campanha
        EtapaCampanha.objects.create(
            campanha=campanha,
            ordem=1,
            nome="E-mail de Boas-vindas",
            tipo="email",
            delay_dias=0,
            assunto="Bem-vindo à Lions CRM!",
            conteudo="<h2>Olá {{lead.nome}},</h2><p>Seja bem-vindo à Lions CRM! Estamos felizes em tê-lo conosco.</p>"
        )
        
        EtapaCampanha.objects.create(
            campanha=campanha,
            ordem=2,
            nome="Material Educativo",
            tipo="email",
            delay_dias=2,
            assunto="Conheça nossos recursos",
            conteudo="<h2>Olá {{lead.nome}},</h2><p>Conheça os principais recursos do nosso sistema...</p>"
        )
        
        EtapaCampanha.objects.create(
            campanha=campanha,
            ordem=3,
            nome="Contato de acompanhamento",
            tipo="tarefa",
            delay_dias=4,
            assunto="Ligar para {{lead.nome}}"
        )
        
        print("Etapas da campanha criadas com sucesso")
        return campanha
    except Exception as e:
        print(f"ERRO ao criar campanha: {str(e)}")
        return None

def criar_criterios_score():
    """Cria critérios de score para teste"""
    try:
        # Critérios demográficos
        CriterioScore.objects.create(
            nome="Cargo de decisão",
            tipo="demografico",
            descricao="Lead com cargo de decisão (Diretor, Gerente, etc)",
            pontos=20,
            condicao='{"campo": "cargo", "valores": ["Diretor", "CEO", "Gerente", "Proprietário"]}'
        )
        
        # Critérios comportamentais
        CriterioScore.objects.create(
            nome="Visita página de preços",
            tipo="comportamental",
            descricao="Lead visitou a página de preços",
            pontos=15,
            condicao='{"evento": "visita_pagina", "pagina": "precos"}'
        )
        
        # Critérios de engajamento
        CriterioScore.objects.create(
            nome="Responde emails",
            tipo="engajamento",
            descricao="Lead responde aos emails",
            pontos=10,
            condicao='{"evento": "responde_email", "minimo": 1}'
        )
        
        # Critérios de interesse
        CriterioScore.objects.create(
            nome="Interesse em produto específico",
            tipo="interesse",
            descricao="Lead mostrou interesse em produto específico",
            pontos=25,
            condicao='{"evento": "interesse_produto"}'
        )
        
        print("Critérios de score criados com sucesso")
    except Exception as e:
        print(f"ERRO ao criar critérios de score: {str(e)}")

def criar_gatilho_teste():
    """Cria um gatilho automático de teste"""
    try:
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            print("ERRO: Nenhum usuário admin encontrado")
            return

        # Precisamos de um workflow para associar ao gatilho
        workflow = Workflow.objects.filter(ativo=True).first()
        if not workflow:
            workflow = criar_workflow_teste()
            if not workflow:
                print("ERRO: Não foi possível criar workflow para o gatilho")
                return
        
        # Criar gatilho
        gatilho = GatilhoAutomatico.objects.create(
            nome="Gatilho para Score Alto",
            evento="score_threshold",
            condicoes='{"score_minimo": 70}',
            workflow=workflow,
            ativo=True
        )
        
        print(f"Gatilho criado: {gatilho.nome}")
        return gatilho
    except Exception as e:
        print(f"ERRO ao criar gatilho: {str(e)}")
        return None

def testar_lead_scoring():
    """Testa o sistema de pontuação de leads"""
    try:
        # Garantir que temos critérios de score
        if CriterioScore.objects.count() == 0:
            criar_criterios_score()
        
        # Pegar um lead aleatório
        lead = Lead.objects.order_by('?').first()
        if not lead:
            print("ERRO: Nenhum lead encontrado para testar")
            return
            
        # Calcular score
        service = LeadScoringService()
        score = service.calcular_score_lead(lead)
        
        print(f"Score calculado para {lead.nome}: {score.pontuacao_total} pontos")
        print(f"Classificação: {score.classificacao}")
        print(f"Detalhes: Demográfico={score.pontos_demograficos}, Comportamental={score.pontos_comportamentais}, " +
              f"Engajamento={score.pontos_engajamento}, Interesse={score.pontos_interesse}")
    except Exception as e:
        print(f"ERRO ao testar lead scoring: {str(e)}")

def testar_execucao_workflow():
    """Testa a execução manual de um workflow"""
    try:
        # Garantir que temos um workflow
        workflow = Workflow.objects.filter(ativo=True).first()
        if not workflow:
            workflow = criar_workflow_teste()
            if not workflow:
                print("ERRO: Não foi possível criar workflow para testar")
                return
        
        # Pegar um lead aleatório
        lead = Lead.objects.order_by('?').first()
        if not lead:
            print("ERRO: Nenhum lead encontrado para testar")
            return
        
        # Executar workflow
        service = WorkflowService()
        execucao = service.executar_workflow(workflow, lead)
        
        print(f"Workflow {workflow.nome} executado para {lead.nome}")
        print(f"Status: {execucao.status}")
    except Exception as e:
        print(f"ERRO ao testar execução de workflow: {str(e)}")

def testar_entrada_campanha():
    """Testa a entrada de leads em campanhas"""
    try:
        # Garantir que temos uma campanha
        campanha = CampanhaNutricao.objects.filter(status="ativa").first()
        if not campanha:
            campanha = criar_campanha_teste()
            if not campanha:
                print("ERRO: Não foi possível criar campanha para testar")
                return
        
        # Processar entradas
        service = CampanhaService()
        leads_processados = service.processar_entradas_campanhas(force=True)
        
        print(f"Processamento de entradas em campanhas concluído")
        print(f"Leads processados: {leads_processados}")
    except Exception as e:
        print(f"ERRO ao testar entrada em campanha: {str(e)}")

def executar_teste_completo():
    """Executa uma série de testes no módulo de automação"""
    print("======== INICIANDO TESTES DO MÓDULO DE AUTOMAÇÃO ========")
    
    try:
        print("\n1. Criando workflow de teste...")
        criar_workflow_teste()
        
        print("\n2. Criando campanha de nutrição de teste...")
        criar_campanha_teste()
        
        print("\n3. Criando critérios de score...")
        criar_criterios_score()
        
        print("\n4. Criando gatilho automático de teste...")
        criar_gatilho_teste()
        
        print("\n5. Testando cálculo de score...")
        testar_lead_scoring()
        
        print("\n6. Testando execução de workflow...")
        testar_execucao_workflow()
        
        print("\n7. Testando entrada em campanha...")
        testar_entrada_campanha()
        
        print("\n======== TESTES CONCLUÍDOS COM SUCESSO ========")
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {str(e)}")
        print(traceback.format_exc())
        print("\n======== TESTES INTERROMPIDOS COM ERRO ========")
        sys.exit(1)

if __name__ == "__main__":
    executar_teste_completo()
