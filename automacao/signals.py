from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from leads.models import Lead
from .models import LeadScore, Workflow, ExecucaoWorkflow, HistoricoAutomacao
from .services import LeadScoringService, WorkflowService

@receiver(post_save, sender=Lead)
def lead_criado_ou_atualizado(sender, instance, created, **kwargs):
    """
    Signal executado quando um lead é criado ou atualizado
    """
    try:
        # Calcular ou atualizar score do lead
        scoring_service = LeadScoringService()
        scoring_service.calcular_score_lead(instance)
        
        # Se for um novo lead, executar workflows de "novo_lead"
        if created:
            workflow_service = WorkflowService()
            workflows = Workflow.objects.filter(
                ativo=True,
                evento_gatilho='novo_lead'
            )
            
            for workflow in workflows:
                if workflow_service.lead_atende_criterios(instance, workflow):
                    workflow_service.executar_workflow(workflow, instance)
                      # Registrar no histórico
                    HistoricoAutomacao.objects.create(
                        tipo='workflow',
                        lead=instance,
                        acao=f'Workflow executado: {workflow.nome}',
                        detalhes=f'Workflow executado automaticamente para novo lead',
                        sucesso=True,
                        workflow=workflow
                    )
        
        # Se o status mudou, executar workflows de "mudanca_status"
        else:
            # Verificar se houve mudança de status
            if hasattr(instance, '_original_status') and instance._original_status != instance.status:
                workflow_service = WorkflowService()
                workflows = Workflow.objects.filter(
                    ativo=True,
                    evento_gatilho='mudanca_status'
                )
                
                for workflow in workflows:
                    # Verificar se o workflow é para este status específico
                    if (workflow.status_lead_alvo and 
                        workflow.status_lead_alvo != instance.status):
                        continue
                        
                    if workflow_service.lead_atende_criterios(instance, workflow):
                        workflow_service.executar_workflow(workflow, instance)
                          # Registrar no histórico
                        HistoricoAutomacao.objects.create(
                            tipo='workflow',
                            lead=instance,
                            acao=f'Workflow executado: {workflow.nome}',
                            detalhes=f'Workflow executado por mudança de status para {instance.get_status_display()}',
                            sucesso=True,
                            workflow=workflow
                        )
    
    except Exception as e:        # Registrar erro no histórico
        HistoricoAutomacao.objects.create(
            tipo='workflow',
            lead=instance,
            acao='Erro de automação',
            detalhes=f'Erro ao processar signals de automação: {str(e)}',
            sucesso=False
        )

@receiver(pre_save, sender=Lead)
def lead_pre_save(sender, instance, **kwargs):
    """
    Signal executado antes de salvar um lead
    Usado para detectar mudanças de status
    """
    if instance.pk:
        try:
            original = Lead.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Lead.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None

@receiver(post_save, sender=LeadScore)
def score_atualizado(sender, instance, created, **kwargs):
    """
    Signal executado quando um score é criado ou atualizado
    """
    try:
        # Executar workflows de "score_atualizado"
        workflow_service = WorkflowService()
        workflows = Workflow.objects.filter(
            ativo=True,
            evento_gatilho='score_atualizado'
        )
        
        for workflow in workflows:
            # Verificar se atende o score mínimo
            if (workflow.score_minimo and 
                instance.score_total < workflow.score_minimo):
                continue
                
            if workflow_service.lead_atende_criterios(instance.lead, workflow):
                workflow_service.executar_workflow(workflow, instance.lead)
                  # Registrar no histórico
                HistoricoAutomacao.objects.create(
                    tipo='workflow',
                    lead=instance.lead,
                    acao=f'Workflow executado: {workflow.nome}',
                    detalhes=f'Workflow executado por atualização de score (Score: {instance.pontuacao_total})',
                    sucesso=True,
                    workflow=workflow
                )
    
    except Exception as e:        # Registrar erro no histórico
        HistoricoAutomacao.objects.create(
            tipo='workflow',
            lead=instance.lead,
            acao='Erro ao processar workflow',
            detalhes=f'Erro ao processar workflow por atualização de score: {str(e)}',
            sucesso=False
        )

# Função para registrar atividade de contato
def registrar_contato_lead(lead, tipo_contato='email'):
    """
    Função para ser chamada quando há um novo contato com o lead
    """
    try:
        # Executar workflows de "novo_contato"
        workflow_service = WorkflowService()
        workflows = Workflow.objects.filter(
            ativo=True,
            evento_gatilho='novo_contato'
        )
        
        for workflow in workflows:
            if workflow_service.lead_atende_criterios(lead, workflow):
                workflow_service.executar_workflow(workflow, lead)
                  # Registrar no histórico
                HistoricoAutomacao.objects.create(
                    tipo='workflow',
                    lead=lead,
                    acao=f'Workflow executado: {workflow.nome}',
                    detalhes=f'Workflow executado por novo contato ({tipo_contato})',
                    sucesso=True,
                    workflow=workflow
                )
                
        # Atualizar score de engajamento
        scoring_service = LeadScoringService()
        scoring_service.calcular_score_lead(lead)
    
    except Exception as e:        # Registrar erro no histórico
        HistoricoAutomacao.objects.create(
            tipo='workflow',
            lead=lead,
            acao='Erro ao processar workflow',
            detalhes=f'Erro ao processar workflow por novo contato ({tipo_contato}): {str(e)}',
            sucesso=False
        )
