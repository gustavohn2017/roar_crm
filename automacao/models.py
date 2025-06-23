"""
Modelos para o sistema de automação de marketing e vendas.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Optional, Any
import json


class LeadScore(models.Model):
    """
    Sistema de pontuação de leads baseado em critérios configuráveis.
    """
    lead = models.OneToOneField(
        'leads.Lead', 
        on_delete=models.CASCADE, 
        related_name='score'
    )
    pontuacao_total = models.IntegerField(default=0)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    
    # Critérios de pontuação
    pontos_demograficos = models.IntegerField(default=0)
    pontos_comportamentais = models.IntegerField(default=0)
    pontos_engajamento = models.IntegerField(default=0)
    pontos_interesse = models.IntegerField(default=0)
    
    # Classificação baseada na pontuação
    CLASSIFICACAO_CHOICES = [
        ('frio', 'Lead Frio (0-30)'),
        ('morno', 'Lead Morno (31-60)'),
        ('quente', 'Lead Quente (61-80)'),
        ('muito_quente', 'Lead Muito Quente (81-100)'),
    ]
    classificacao = models.CharField(
        max_length=20, 
        choices=CLASSIFICACAO_CHOICES, 
        default='frio'
    )
    
    class Meta:
        verbose_name = "Pontuação de Lead"
        verbose_name_plural = "Pontuações de Leads"
        ordering = ['-pontuacao_total']
    
    def __str__(self):
        return f"{self.lead.nome} - {self.pontuacao_total} pontos"
    
    def calcular_pontuacao(self) -> int:
        """Calcula a pontuação total baseada nos critérios."""
        self.pontuacao_total = (
            self.pontos_demograficos + 
            self.pontos_comportamentais + 
            self.pontos_engajamento + 
            self.pontos_interesse
        )
        self.atualizar_classificacao()
        self.save()
        return self.pontuacao_total
    
    def atualizar_classificacao(self):
        """Atualiza a classificação baseada na pontuação total."""
        if self.pontuacao_total <= 30:
            self.classificacao = 'frio'
        elif self.pontuacao_total <= 60:
            self.classificacao = 'morno'
        elif self.pontuacao_total <= 80:
            self.classificacao = 'quente'
        else:
            self.classificacao = 'muito_quente'


class CriterioScore(models.Model):
    """
    Critérios configuráveis para pontuação de leads.
    """
    TIPO_CHOICES = [
        ('demografico', 'Demográfico'),
        ('comportamental', 'Comportamental'),
        ('engajamento', 'Engajamento'),
        ('interesse', 'Interesse'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField(blank=True)
    pontos = models.IntegerField(default=0)
    condicao = models.TextField(
        help_text="Condição em formato JSON para avaliação automática"
    )
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Critério de Pontuação"
        verbose_name_plural = "Critérios de Pontuação"
    
    def __str__(self):
        return f"{self.nome} ({self.pontos} pontos)"


class Workflow(models.Model):
    """
    Sistema de workflows automatizados para leads.
    """
    TRIGGER_CHOICES = [
        ('lead_criado', 'Lead Criado'),
        ('status_alterado', 'Status Alterado'),
        ('sem_contato', 'Sem Contato por X dias'),
        ('score_alterado', 'Score Alterado'),
        ('data_especifica', 'Data Específica'),
        ('acao_manual', 'Ação Manual'),
    ]
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES)
    condicoes = models.TextField(
        blank=True,
        help_text="Condições em formato JSON para execução do workflow"
    )
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return self.nome


class AcaoWorkflow(models.Model):
    """
    Ações específicas dentro de um workflow.
    """
    TIPO_ACAO_CHOICES = [
        ('enviar_email', 'Enviar E-mail'),
        ('enviar_whatsapp', 'Enviar WhatsApp'),
        ('criar_tarefa', 'Criar Tarefa'),
        ('alterar_status', 'Alterar Status'),
        ('atribuir_vendedor', 'Atribuir Vendedor'),
        ('aguardar', 'Aguardar X dias'),
        ('notificar_usuario', 'Notificar Usuário'),
    ]
    
    workflow = models.ForeignKey(
        Workflow, 
        on_delete=models.CASCADE, 
        related_name='acoes'
    )
    ordem = models.IntegerField(default=1)
    tipo_acao = models.CharField(max_length=20, choices=TIPO_ACAO_CHOICES)
    parametros = models.TextField(
        help_text="Parâmetros da ação em formato JSON"
    )
    delay_dias = models.IntegerField(
        default=0, 
        help_text="Delay em dias antes de executar esta ação"
    )
    condicoes = models.TextField(
        blank=True,
        help_text="Condições específicas para esta ação"
    )
    
    class Meta:
        verbose_name = "Ação do Workflow"
        verbose_name_plural = "Ações dos Workflows"
        ordering = ['workflow', 'ordem']
    
    def __str__(self):
        return f"{self.workflow.nome} - {self.get_tipo_acao_display()}"


class CampanhaNutricao(models.Model):
    """
    Campanhas de nutrição de leads com sequência de comunicações.
    """
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('pausada', 'Pausada'),
        ('concluida', 'Concluída'),
        ('rascunho', 'Rascunho'),
    ]
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    objetivo = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    # Critérios de segmentação
    criterios_segmentacao = models.TextField(
        blank=True,
        help_text="Critérios para incluir leads na campanha (JSON)"
    )
    
    class Meta:
        verbose_name = "Campanha de Nutrição"
        verbose_name_plural = "Campanhas de Nutrição"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return self.nome


class EtapaCampanha(models.Model):
    """
    Etapas individuais de uma campanha de nutrição.
    """
    TIPO_CHOICES = [
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
        ('tarefa', 'Tarefa para Vendedor'),
        ('aguardar', 'Aguardar'),
    ]
    
    campanha = models.ForeignKey(
        CampanhaNutricao, 
        on_delete=models.CASCADE, 
        related_name='etapas'
    )
    ordem = models.IntegerField()
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    delay_dias = models.IntegerField(
        default=0, 
        help_text="Dias após a etapa anterior"
    )
      # Conteúdo da comunicação
    assunto = models.CharField(max_length=500, blank=True)
    conteudo = models.TextField(blank=True)
    template = models.ForeignKey(
        'leads.TemplateComunitacao', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='email_etapas'
    )
    template_whatsapp = models.ForeignKey(
        'leads.TemplateComunitacao', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='whatsapp_etapas'
    )
    
    # Condições de envio
    condicoes = models.TextField(
        blank=True,
        help_text="Condições para executar esta etapa (JSON)"
    )
    
    class Meta:
        verbose_name = "Etapa da Campanha"
        verbose_name_plural = "Etapas das Campanhas"
        ordering = ['campanha', 'ordem']
    
    def __str__(self):
        return f"{self.campanha.nome} - Etapa {self.ordem}"


class ExecucaoWorkflow(models.Model):
    """
    Registro de execuções de workflows para tracking.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('executando', 'Executando'),
        ('concluido', 'Concluído'),
        ('erro', 'Erro'),
        ('cancelado', 'Cancelado'),
    ]
    
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    data_proxima_acao = models.DateTimeField(null=True, blank=True)
    acao_atual = models.IntegerField(default=1)
    log_execucao = models.TextField(blank=True)
    erro_detalhes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Execução de Workflow"
        verbose_name_plural = "Execuções de Workflows"
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.workflow.nome} - {self.lead.nome}"


class ParticipacaoCampanha(models.Model):
    """
    Registro de participação de leads em campanhas de nutrição.
    """
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('pausada', 'Pausada'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    campanha = models.ForeignKey(CampanhaNutricao, on_delete=models.CASCADE)
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa')
    data_entrada = models.DateTimeField(auto_now_add=True)
    etapa_atual = models.IntegerField(default=1)
    data_proxima_etapa = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Participação em Campanha"
        verbose_name_plural = "Participações em Campanhas"
        unique_together = ['campanha', 'lead']
        ordering = ['-data_entrada']
    
    def __str__(self):
        return f"{self.lead.nome} - {self.campanha.nome}"


class GatilhoAutomatico(models.Model):
    """
    Gatilhos automáticos baseados em eventos do sistema.
    """
    EVENTO_CHOICES = [
        ('lead_criado', 'Lead Criado'),
        ('contato_realizado', 'Contato Realizado'),
        ('status_alterado', 'Status do Lead Alterado'),
        ('sem_atividade', 'Sem Atividade há X dias'),
        ('score_threshold', 'Score Atingiu Threshold'),
        ('data_vencimento', 'Data de Vencimento'),
        ('email_aberto', 'E-mail Aberto'),
        ('link_clicado', 'Link Clicado'),
    ]
    
    nome = models.CharField(max_length=200)
    evento = models.CharField(max_length=20, choices=EVENTO_CHOICES)
    condicoes = models.TextField(
        help_text="Condições em formato JSON para ativação do gatilho"
    )
    workflow = models.ForeignKey(
        Workflow, 
        on_delete=models.CASCADE,
        help_text="Workflow a ser executado quando o gatilho for ativado"
    )
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Gatilho Automático"
        verbose_name_plural = "Gatilhos Automáticos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome} - {self.get_evento_display()}"


class HistoricoAutomacao(models.Model):
    """
    Histórico de todas as ações automáticas executadas.
    """
    TIPO_CHOICES = [
        ('workflow', 'Workflow'),
        ('campanha', 'Campanha de Nutrição'),
        ('gatilho', 'Gatilho Automático'),
        ('score', 'Atualização de Score'),
    ]
    
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    acao = models.CharField(max_length=200)
    detalhes = models.TextField(blank=True)
    sucesso = models.BooleanField(default=True)
    data_execucao = models.DateTimeField(auto_now_add=True)
    
    # Referencias opcionais
    workflow = models.ForeignKey(Workflow, on_delete=models.SET_NULL, null=True, blank=True)
    campanha = models.ForeignKey(CampanhaNutricao, on_delete=models.SET_NULL, null=True, blank=True)
    gatilho = models.ForeignKey(GatilhoAutomatico, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Histórico de Automação"
        verbose_name_plural = "Histórico de Automações"
        ordering = ['-data_execucao']
    
    def __str__(self):
        return f"{self.lead.nome} - {self.acao}"
