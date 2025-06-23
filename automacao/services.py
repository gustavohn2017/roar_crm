"""
Serviços para automação de marketing e vendas.
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

from leads.models import Lead
from vendedores.models import TentativaContato, Nota, Evento
from .models import (
    LeadScore, CriterioScore, Workflow, AcaoWorkflow, 
    CampanhaNutricao, EtapaCampanha, ExecucaoWorkflow,
    ParticipacaoCampanha, GatilhoAutomatico, HistoricoAutomacao
)


class LeadScoringService:
    """
    Serviço para cálculo e atualização de lead scoring.
    """
    @staticmethod
    def calcular_score_lead(lead: Lead) -> LeadScore:
        """
        Calcula o score completo de um lead baseado em todos os critérios.
        Retorna o objeto LeadScore atualizado.
        """
        score, created = LeadScore.objects.get_or_create(lead=lead)
        
        # Reset dos pontos
        score.pontos_demograficos = 0
        score.pontos_comportamentais = 0
        score.pontos_engajamento = 0
        score.pontos_interesse = 0
        
        # Aplicar critérios demográficos
        score.pontos_demograficos = LeadScoringService._calcular_pontos_demograficos(lead)
        
        # Aplicar critérios comportamentais
        score.pontos_comportamentais = LeadScoringService._calcular_pontos_comportamentais(lead)
        
        # Aplicar critérios de engajamento
        score.pontos_engajamento = LeadScoringService._calcular_pontos_engajamento(lead)
        
        # Aplicar critérios de interesse
        score.pontos_interesse = LeadScoringService._calcular_pontos_interesse(lead)
        
        # Calcular pontuação total
        pontuacao_total = score.calcular_pontuacao()
        
        # Registrar no histórico
        HistoricoAutomacao.objects.create(
            lead=lead,
            tipo='score',
            acao=f'Score atualizado para {pontuacao_total}',
            detalhes=f'Demográfico: {score.pontos_demograficos}, '
                    f'Comportamental: {score.pontos_comportamentais}, '
                    f'Engajamento: {score.pontos_engajamento}, '
                    f'Interesse: {score.pontos_interesse}'
        )
        
        return score
    
    @staticmethod
    def _calcular_pontos_demograficos(lead: Lead) -> int:
        """Calcula pontos baseados em dados demográficos."""
        pontos = 0
        
        # Pontos por informações completas
        if lead.email:
            pontos += 10
        if lead.telefone:
            pontos += 10
        if lead.empresa:
            pontos += 15
        if lead.cargo:
            pontos += 10
        if lead.faturamento_mensal:
            pontos += 20
            # Pontos extras por faturamento alto
            if lead.faturamento_mensal > 100000:
                pontos += 15
            elif lead.faturamento_mensal > 50000:
                pontos += 10
        
        return min(pontos, 50)  # Máximo 50 pontos demográficos
    
    @staticmethod
    def _calcular_pontos_comportamentais(lead: Lead) -> int:
        """Calcula pontos baseados em comportamento."""
        pontos = 0
        
        # Pontos por contatos bem-sucedidos
        contatos_sucesso = TentativaContato.objects.filter(
            lead=lead, 
            resultado='sucesso'
        ).count()
        pontos += min(contatos_sucesso * 5, 25)
        
        # Pontos por rapidez de resposta (se respondeu em menos de 24h)
        primeiro_contato = TentativaContato.objects.filter(lead=lead).first()
        if primeiro_contato:
            tempo_resposta = primeiro_contato.data_hora - lead.data_criacao
            if tempo_resposta.days == 0:
                pontos += 15
        
        return min(pontos, 30)  # Máximo 30 pontos comportamentais
    
    @staticmethod
    def _calcular_pontos_engajamento(lead: Lead) -> int:
        """Calcula pontos baseados em engajamento."""
        pontos = 0
        
        # Pontos por progressão no funil
        status_pontos = {
            'novo': 0,
            'contatado': 5,
            'qualificado': 15,
            'proposta': 25,
            'negociacao': 35,
            'fechado': 50
        }
        pontos += status_pontos.get(lead.status, 0)
        
        # Pontos por atividade recente
        dias_sem_atividade = (timezone.now() - lead.data_ultimo_contato).days if lead.data_ultimo_contato else 999
        if dias_sem_atividade <= 7:
            pontos += 10
        elif dias_sem_atividade <= 30:
            pontos += 5
        
        return min(pontos, 40)  # Máximo 40 pontos de engajamento
    
    @staticmethod
    def _calcular_pontos_interesse(lead: Lead) -> int:
        """Calcula pontos baseados em interesse demonstrado."""
        pontos = 0
        
        # Pontos por valor de interesse
        if lead.valor_interesse:
            if lead.valor_interesse >= 500000:
                pontos += 30
            elif lead.valor_interesse >= 100000:
                pontos += 20
            elif lead.valor_interesse >= 50000:
                pontos += 15
            else:
                pontos += 10
        
        # Pontos por tipo de interesse (alguns produtos são mais qualificados)
        interesse_pontos = {
            'consorcio': 15,
            'financiamento': 20,
            'carta_credito': 25,
            'capital_giro': 20,
            'emprestimo': 10,
            'outro': 5
        }
        pontos += interesse_pontos.get(lead.interesse, 0)
        
        # Pontos por prioridade
        if lead.prioridade == 3:  # Alta
            pontos += 15
        elif lead.prioridade == 2:  # Média
            pontos += 10
        
        return min(pontos, 50)  # Máximo 50 pontos de interesse


class WorkflowService:
    """
    Serviço para execução de workflows automatizados.
    """
    
    @staticmethod
    def executar_workflow(workflow: Workflow, lead: Lead) -> ExecucaoWorkflow:
        """
        Inicia a execução de um workflow para um lead específico.
        """
        execucao = ExecucaoWorkflow.objects.create(
            workflow=workflow,
            lead=lead,
            status='pendente'
        )
        
        try:
            WorkflowService._processar_proxima_acao(execucao)
        except Exception as e:
            execucao.status = 'erro'
            execucao.erro_detalhes = str(e)
            execucao.save()
        
        return execucao
    
    @staticmethod
    def _processar_proxima_acao(execucao: ExecucaoWorkflow):
        """
        Processa a próxima ação do workflow.
        """
        acoes = execucao.workflow.acoes.filter(ordem=execucao.acao_atual)
        
        if not acoes.exists():
            # Workflow concluído
            execucao.status = 'concluido'
            execucao.data_conclusao = timezone.now()
            execucao.save()
            return
        
        acao = acoes.first()
        execucao.status = 'executando'
        execucao.save()
        
        # Verificar delay
        if acao.delay_dias > 0:
            execucao.data_proxima_acao = timezone.now() + timedelta(days=acao.delay_dias)
            execucao.save()
            return
        
        # Executar ação
        sucesso = WorkflowService._executar_acao(acao, execucao.lead)
        
        if sucesso:
            execucao.acao_atual += 1
            execucao.log_execucao += f"\n[{timezone.now()}] Ação {acao.tipo_acao} executada com sucesso"
            WorkflowService._processar_proxima_acao(execucao)
        else:
            execucao.status = 'erro'
            execucao.erro_detalhes = f"Falha ao executar ação: {acao.tipo_acao}"
            execucao.save()
    
    @staticmethod
    def _executar_acao(acao: AcaoWorkflow, lead: Lead) -> bool:
        """
        Executa uma ação específica do workflow.
        """
        try:
            parametros = json.loads(acao.parametros) if acao.parametros else {}
            
            if acao.tipo_acao == 'enviar_email':
                return WorkflowService._enviar_email(lead, parametros)
            elif acao.tipo_acao == 'enviar_whatsapp':
                return WorkflowService._enviar_whatsapp(lead, parametros)
            elif acao.tipo_acao == 'criar_tarefa':
                return WorkflowService._criar_tarefa(lead, parametros)
            elif acao.tipo_acao == 'alterar_status':
                return WorkflowService._alterar_status(lead, parametros)
            elif acao.tipo_acao == 'atribuir_vendedor':
                return WorkflowService._atribuir_vendedor(lead, parametros)
            elif acao.tipo_acao == 'notificar_usuario':
                return WorkflowService._notificar_usuario(lead, parametros)
            
            return True
        except Exception as e:
            print(f"Erro ao executar ação {acao.tipo_acao}: {e}")
            return False
    
    @staticmethod
    def _enviar_email(lead: Lead, parametros: Dict) -> bool:
        """Envia e-mail para o lead."""
        try:
            assunto = parametros.get('assunto', 'Mensagem automática')
            corpo = parametros.get('corpo', '')
            
            # Personalizar mensagem
            corpo = corpo.replace('{nome}', lead.nome)
            corpo = corpo.replace('{empresa}', lead.empresa or '')
            
            send_mail(
                subject=assunto,
                message=corpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                fail_silently=False
            )
            
            # Registrar no histórico
            HistoricoAutomacao.objects.create(
                lead=lead,
                tipo='workflow',
                acao='E-mail enviado automaticamente',
                detalhes=f'Assunto: {assunto}'
            )
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def _enviar_whatsapp(lead: Lead, parametros: Dict) -> bool:
        """Prepara mensagem de WhatsApp (implementação depende da API escolhida)."""
        # Por enquanto, apenas cria uma nota para o vendedor
        mensagem = parametros.get('mensagem', '')
        mensagem = mensagem.replace('{nome}', lead.nome)
        
        Nota.objects.create(
            titulo=f"WhatsApp para {lead.nome}",
            conteudo=f"Mensagem automática: {mensagem}",
            vendedor=lead.responsavel or User.objects.filter(is_staff=True).first(),
            lead=lead,
            tipo='lembrete',
            prioridade=2
        )
        
        return True
    
    @staticmethod
    def _criar_tarefa(lead: Lead, parametros: Dict) -> bool:
        """Cria uma tarefa para o vendedor responsável."""
        titulo = parametros.get('titulo', f'Tarefa para {lead.nome}')
        descricao = parametros.get('descricao', '')
        
        vendedor = lead.responsavel or User.objects.filter(is_staff=True).first()
        
        Evento.objects.create(
            titulo=titulo,
            descricao=descricao,
            data=timezone.now().date() + timedelta(days=1),
            hora=timezone.now().time(),
            tipo='other',
            vendedor=vendedor,
            lead=lead
        )
        
        return True
    
    @staticmethod
    def _alterar_status(lead: Lead, parametros: Dict) -> bool:
        """Altera o status do lead."""
        novo_status = parametros.get('status')
        if novo_status and novo_status in dict(Lead.STATUS_CHOICES):
            lead.status = novo_status
            lead.save()
            return True
        return False
    
    @staticmethod
    def _atribuir_vendedor(lead: Lead, parametros: Dict) -> bool:
        """Atribui um vendedor ao lead."""
        vendedor_id = parametros.get('vendedor_id')
        if vendedor_id:
            try:
                vendedor = User.objects.get(id=vendedor_id)
                lead.responsavel = vendedor
                lead.save()
                return True
            except User.DoesNotExist:
                pass
        return False
    
    @staticmethod
    def _notificar_usuario(lead: Lead, parametros: Dict) -> bool:
        """Notifica um usuário específico."""
        # Implementação básica - criar uma nota
        usuario_id = parametros.get('usuario_id')
        mensagem = parametros.get('mensagem', f'Notificação sobre {lead.nome}')
        
        try:
            usuario = User.objects.get(id=usuario_id)
            Nota.objects.create(
                titulo=f"Notificação: {lead.nome}",
                conteudo=mensagem,
                vendedor=usuario,
                lead=lead,
                tipo='lembrete',
                prioridade=3
            )
            return True
        except User.DoesNotExist:
            return False


class CampanhaService:
    """
    Serviço para gestão de campanhas de nutrição.
    """
    
    def processar_entradas_campanhas(self, force=False):
        """
        Processa leads que devem entrar em campanhas de nutrição.
        
        Args:
            force (bool): Se True, força a verificação de todos os leads para todas campanhas
                          ignorando critérios temporais
                          
        Returns:
            int: Número de leads processados
        """
        # Obter todas as campanhas ativas
        campanhas = CampanhaNutricao.objects.filter(
            status='ativa',
            data_inicio__lte=timezone.now()
        )
        
        if not campanhas:
            return 0
            
        leads_processados = 0
        
        # Para cada campanha, verificar leads que devem entrar
        for campanha in campanhas:
            try:
                criterios = {}
                
                # Converter critérios da campanha de JSON para dict
                if campanha.criterios_segmentacao:
                    try:
                        criterios = json.loads(campanha.criterios_segmentacao)
                    except:
                        pass
                
                # Construir query de leads que atendem aos critérios
                queryset = Lead.objects.all()
                
                # Filtrar por status se especificado
                if 'status' in criterios and criterios['status']:
                    if isinstance(criterios['status'], list):
                        queryset = queryset.filter(status__in=criterios['status'])
                    else:
                        queryset = queryset.filter(status=criterios['status'])
                
                # Filtrar leads que já participam da campanha
                leads_existentes = ParticipacaoCampanha.objects.filter(
                    campanha=campanha
                ).values_list('lead_id', flat=True)
                
                queryset = queryset.exclude(id__in=leads_existentes)
                
                # Processar leads encontrados
                for lead in queryset:
                    # Verificar critérios adicionais aqui se necessário
                    self.adicionar_lead_campanha(campanha, lead)
                    leads_processados += 1
                    
                    # Registrar no histórico
                    HistoricoAutomacao.objects.create(
                        tipo='campanha',
                        lead=lead,
                        acao=f'Incluído automaticamente na campanha: {campanha.nome}',
                        campanha=campanha,
                        sucesso=True
                    )
            
            except Exception as e:
                # Registrar erro no histórico
                HistoricoAutomacao.objects.create(
                    tipo='campanha',
                    acao=f'Erro ao processar entradas na campanha: {campanha.nome}',
                    sucesso=False,
                    campanha=campanha,
                    detalhes=str(e)
                )
        
        return leads_processados
    
    @staticmethod
    def adicionar_lead_campanha(campanha: CampanhaNutricao, lead: Lead) -> ParticipacaoCampanha:
        """
        Adiciona um lead a uma campanha de nutrição.
        """
        participacao, created = ParticipacaoCampanha.objects.get_or_create(
            campanha=campanha,
            lead=lead,
            defaults={
                'etapa_atual': 1,
                'data_proxima_etapa': timezone.now()
            }
        )
        
        if created:
            HistoricoAutomacao.objects.create(
                lead=lead,
                tipo='campanha',
                acao=f'Adicionado à campanha: {campanha.nome}',
                campanha=campanha
            )
        
        return participacao
    
    @staticmethod
    def processar_campanhas_pendentes():
        """
        Processa todas as campanhas com etapas pendentes.
        """
        participacoes_pendentes = ParticipacaoCampanha.objects.filter(
            status='ativa',
            data_proxima_etapa__lte=timezone.now()        )
        
        for participacao in participacoes_pendentes:
            CampanhaService._executar_etapa_campanha(participacao)
    
    @staticmethod
    def executar_proxima_etapa(participacao: ParticipacaoCampanha):
        """
        Executa a próxima etapa da campanha para um lead.
        """
        return CampanhaService._executar_etapa_campanha(participacao)
    
    @staticmethod
    def _executar_etapa_campanha(participacao: ParticipacaoCampanha):
        """
        Executa uma etapa específica da campanha para um lead.
        """
        etapa = participacao.campanha.etapas.filter(
            ordem=participacao.etapa_atual
        ).first()
        
        if not etapa:
            # Campanha concluída
            participacao.status = 'concluida'
            participacao.data_conclusao = timezone.now()
            participacao.save()
            return
        
        # Executar ação da etapa
        sucesso = False
        if etapa.tipo == 'email':
            sucesso = CampanhaService._enviar_email_campanha(participacao.lead, etapa)
        elif etapa.tipo == 'whatsapp':
            sucesso = CampanhaService._enviar_whatsapp_campanha(participacao.lead, etapa)
        elif etapa.tipo == 'tarefa':
            sucesso = CampanhaService._criar_tarefa_campanha(participacao.lead, etapa)
        
        if sucesso:
            # Avançar para próxima etapa
            participacao.etapa_atual += 1
            proxima_etapa = participacao.campanha.etapas.filter(
                ordem=participacao.etapa_atual
            ).first()
            
            if proxima_etapa:
                participacao.data_proxima_etapa = timezone.now() + timedelta(
                    days=proxima_etapa.delay_dias
                )
            else:
                participacao.status = 'concluida'
                participacao.data_conclusao = timezone.now()
            
            participacao.save()
            
            # Registrar no histórico
            HistoricoAutomacao.objects.create(
                lead=participacao.lead,
                tipo='campanha',
                acao=f'Etapa {etapa.ordem} executada: {etapa.nome}',
                campanha=participacao.campanha
            )
    
    @staticmethod
    def _enviar_email_campanha(lead: Lead, etapa: EtapaCampanha) -> bool:
        """Envia e-mail da campanha."""
        try:
            assunto = etapa.assunto.replace('{nome}', lead.nome)
            conteudo = etapa.conteudo.replace('{nome}', lead.nome)
            conteudo = conteudo.replace('{empresa}', lead.empresa or '')
            
            send_mail(
                subject=assunto,
                message=conteudo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                fail_silently=False
            )
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def _enviar_whatsapp_campanha(lead: Lead, etapa: EtapaCampanha) -> bool:
        """Prepara WhatsApp da campanha."""
        # Implementação similar ao workflow
        mensagem = etapa.conteudo.replace('{nome}', lead.nome)
        
        Nota.objects.create(
            titulo=f"WhatsApp - {etapa.campanha.nome}",
            conteudo=f"Etapa {etapa.ordem}: {mensagem}",
            vendedor=lead.responsavel or User.objects.filter(is_staff=True).first(),
            lead=lead,
            tipo='lembrete',
            prioridade=2
        )
        
        return True
    
    @staticmethod
    def _criar_tarefa_campanha(lead: Lead, etapa: EtapaCampanha) -> bool:
        """Cria tarefa da campanha."""
        vendedor = lead.responsavel or User.objects.filter(is_staff=True).first()
        
        Evento.objects.create(
            titulo=f"{etapa.campanha.nome} - {etapa.nome}",
            descricao=etapa.conteudo,
            data=timezone.now().date() + timedelta(days=1),
            hora=timezone.now().time(),
            tipo='other',
            vendedor=vendedor,
            lead=lead
        )
        
        return True


class GatilhoService:
    """
    Serviço para gestão de gatilhos automáticos.
    """
    
    @staticmethod
    def verificar_gatilhos(evento: str, lead: Lead, **kwargs):
        """
        Verifica e executa gatilhos baseados em eventos.
        """
        gatilhos = GatilhoAutomatico.objects.filter(
            evento=evento,
            ativo=True
        )
        
        for gatilho in gatilhos:
            if GatilhoService._avaliar_condicoes(gatilho, lead, **kwargs):
                WorkflowService.executar_workflow(gatilho.workflow, lead)
                
                HistoricoAutomacao.objects.create(
                    lead=lead,
                    tipo='gatilho',
                    acao=f'Gatilho ativado: {gatilho.nome}',
                    gatilho=gatilho
                )
    
    @staticmethod
    def _avaliar_condicoes(gatilho: GatilhoAutomatico, lead: Lead, **kwargs) -> bool:
        """
        Avalia se as condições do gatilho foram atendidas.
        """
        try:
            condicoes = json.loads(gatilho.condicoes) if gatilho.condicoes else {}
            
            # Implementar lógica de avaliação de condições
            # Por exemplo: verificar status, score, tempo sem atividade, etc.
            
            if 'status_requerido' in condicoes:
                if lead.status != condicoes['status_requerido']:
                    return False
            
            if 'score_minimo' in condicoes:
                score = getattr(lead, 'score', None)
                if not score or score.pontuacao_total < condicoes['score_minimo']:
                    return False
            
            if 'dias_sem_atividade' in condicoes:
                if lead.data_ultimo_contato:
                    dias = (timezone.now() - lead.data_ultimo_contato).days
                    if dias < condicoes['dias_sem_atividade']:
                        return False
            
            return True
        except Exception:
            return False
