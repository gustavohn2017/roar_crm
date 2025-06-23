"""
Comando para execução de workflows programados.
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from automacao.models import Workflow, ExecucaoWorkflow, HistoricoAutomacao, ParticipacaoCampanha
from automacao.services import WorkflowService, CampanhaService
from leads.models import Lead

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Executa workflows programados e etapas de campanhas de nutrição'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force', 
            action='store_true', 
            help='Força a execução de todos os workflows e campanhas',
        )
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.SUCCESS(
            f'Iniciando execução automática em {timezone.now()}'
        ))
        
        try:
            self.processar_workflows_pendentes(force)
            self.processar_execucoes_pendentes()
            self.processar_campanhas_nutricao(force)
            self.processar_campanhas_pendentes()
            
            self.stdout.write(self.style.SUCCESS(
                f'Execução automática concluída com sucesso!'
            ))
        except Exception as e:
            logger.error(f"Erro ao executar tarefas agendadas: {str(e)}", exc_info=True)
            self.stdout.write(self.style.ERROR(
                f'Erro na execução automática: {str(e)}'
            ))
    
    def processar_workflows_pendentes(self, force=False):
        """Processa leads sem workflows ativos ou conforme regras de gatilho"""
        self.stdout.write("Processando workflows pendentes...")
        
        # Verificar workflows de 'sem_contato'
        workflows_sem_contato = Workflow.objects.filter(
            ativo=True, 
            trigger='sem_contato'
        )
        
        leads_processados = 0
        workflow_service = WorkflowService()
        
        for workflow in workflows_sem_contato:
            # Extrair dias para considerar sem contato
            dias_sem_contato = 7  # Valor padrão
            try:
                condicoes = workflow.condicoes
                if condicoes and 'dias_sem_contato' in condicoes:
                    dias_sem_contato = int(condicoes['dias_sem_contato'])
            except:
                pass
            
            # Encontrar leads sem contato pelo período configurado
            data_limite = timezone.now() - timedelta(days=dias_sem_contato)
            
            # Obter leads sem contato recente que não foram processados por este workflow
            leads_sem_contato = Lead.objects.filter(
                data_ultimo_contato__lt=data_limite
            ).exclude(
                execucaoworkflow__workflow=workflow,
                execucaoworkflow__data_inicio__gt=data_limite
            )
            
            for lead in leads_sem_contato:
                if workflow_service.lead_atende_criterios(lead, workflow):
                    workflow_service.executar_workflow(workflow, lead)
                    leads_processados += 1
                    
                    # Registrar no histórico
                    HistoricoAutomacao.objects.create(
                        tipo='workflow',
                        lead=lead,
                        acao=f'Workflow "{workflow.nome}" executado automaticamente (sem contato há {dias_sem_contato} dias)',
                        sucesso=True,
                        workflow=workflow
                    )
            
        self.stdout.write(self.style.SUCCESS(
            f"Processados {leads_processados} leads para workflows pendentes"
        ))
            
    def processar_execucoes_pendentes(self):
        """Processa execuções de workflow que estão aguardando próxima ação"""
        self.stdout.write("Processando execuções de workflow pendentes...")
        
        # Obter execuções pendentes com próxima ação agendada
        execucoes_pendentes = ExecucaoWorkflow.objects.filter(
            status='executando',
            data_proxima_acao__lte=timezone.now()
        )
        
        workflow_service = WorkflowService()
        
        for execucao in execucoes_pendentes:
            workflow_service.continuar_workflow(execucao)
            
        self.stdout.write(self.style.SUCCESS(
            f"Processadas {execucoes_pendentes.count()} execuções pendentes"
        ))
    
    def processar_campanhas_nutricao(self, force=False):
        """Verificar leads que devem entrar em campanhas de nutrição"""
        self.stdout.write("Processando entradas em campanhas de nutrição...")
        
        # Inicializar serviço de campanhas
        campanha_service = CampanhaService()
        campanhas_processadas = campanha_service.processar_entradas_campanhas(force)
            
        self.stdout.write(self.style.SUCCESS(
            f"Processados {campanhas_processadas} leads para entrada em campanhas"
        ))
        
    def processar_campanhas_pendentes(self):
        """Processa etapas pendentes de campanhas de nutrição"""
        self.stdout.write("Processando etapas de campanhas pendentes...")
        
        # Obter participações com próxima etapa agendada
        participacoes_pendentes = ParticipacaoCampanha.objects.filter(
            status='ativa',
            data_proxima_etapa__lte=timezone.now()
        )
        
        campanha_service = CampanhaService()
        
        for participacao in participacoes_pendentes:
            campanha_service.executar_proxima_etapa(participacao)
            
        self.stdout.write(self.style.SUCCESS(
            f"Processadas {participacoes_pendentes.count()} etapas de campanhas"
        ))
