"""
Views para o sistema de automação de marketing e vendas.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Max
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command

from gerencia.decorators import supervisor_or_admin_required
from .models import (
    LeadScore, CriterioScore, Workflow, AcaoWorkflow,
    CampanhaNutricao, EtapaCampanha, ExecucaoWorkflow,
    ParticipacaoCampanha, GatilhoAutomatico, HistoricoAutomacao
)
from .forms import (
    WorkflowForm, AcaoWorkflowForm, CampanhaNutricaoForm,
    EtapaCampanhaForm, GatilhoAutomaticoForm, CriterioScoreForm
)
from .services import LeadScoringService, WorkflowService, CampanhaService, GatilhoService
from leads.models import Lead


@supervisor_or_admin_required
def dashboard_automacao(request):
    """
    Dashboard principal do sistema de automação.
    """
    # Estatísticas gerais
    total_workflows = Workflow.objects.filter(ativo=True).count()
    total_campanhas = CampanhaNutricao.objects.filter(status='ativa').count()
    total_gatilhos = GatilhoAutomatico.objects.filter(ativo=True).count()
    
    # Execuções recentes
    execucoes_hoje = ExecucaoWorkflow.objects.filter(
        data_inicio__date=timezone.now().date()
    ).count()
    
    # Leads por classificação de score
    scores_por_classificacao = LeadScore.objects.values('classificacao').annotate(
        count=Count('id')
    )
    
    # Campanhas ativas com participantes
    campanhas_ativas = CampanhaNutricao.objects.filter(
        status='ativa'
    ).annotate(
        participantes=Count('participacaocampanha')
    )[:5]
    
    # Histórico recente
    historico_recente = HistoricoAutomacao.objects.select_related(
        'lead', 'workflow', 'campanha', 'gatilho'
    ).order_by('-data_execucao')[:10]
    
    context = {
        'total_workflows': total_workflows,
        'total_campanhas': total_campanhas,
        'total_gatilhos': total_gatilhos,
        'execucoes_hoje': execucoes_hoje,
        'scores_por_classificacao': scores_por_classificacao,
        'campanhas_ativas': campanhas_ativas,
        'historico_recente': historico_recente,
    }
    
    return render(request, 'automacao/dashboard.html', context)


@supervisor_or_admin_required
def lista_workflows(request):
    """
    Lista todos os workflows do sistema.
    """
    workflows = Workflow.objects.all().order_by('-data_criacao')
    
    # Filtros
    search_term = request.GET.get('search', '')
    if search_term:
        workflows = workflows.filter(
            Q(nome__icontains=search_term) |
            Q(descricao__icontains=search_term)
        )
    
    trigger_filter = request.GET.get('trigger', '')
    if trigger_filter:
        workflows = workflows.filter(trigger=trigger_filter)
    
    ativo_filter = request.GET.get('ativo', '')
    if ativo_filter:
        workflows = workflows.filter(ativo=ativo_filter == 'true')
      # Paginação
    paginator = Paginator(workflows, 20)
    page = request.GET.get('page')
    workflows = paginator.get_page(page)
    
    context = {
        'workflows': workflows,
        'trigger_choices': Workflow.TRIGGER_CHOICES,
        'search_term': search_term,
        'trigger_filter': trigger_filter,
        'ativo_filter': ativo_filter,
    }
    
    return render(request, 'automacao/workflow_list.html', context)


@supervisor_or_admin_required
def criar_workflow(request):
    """
    Cria um novo workflow.
    """
    if request.method == 'POST':
        form = WorkflowForm(request.POST)
        if form.is_valid():
            workflow = form.save(commit=False)
            workflow.criado_por = request.user
            workflow.save()
            
            messages.success(request, f'Workflow "{workflow.nome}" criado com sucesso!')
            return redirect('automacao:editar_workflow', workflow_id=workflow.id)
    else:
        form = WorkflowForm()
    
    return render(request, 'automacao/workflows/criar.html', {'form': form})


@supervisor_or_admin_required
def editar_workflow(request, workflow_id):
    """
    Edita um workflow existente e suas ações.
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    if request.method == 'POST':
        form = WorkflowForm(request.POST, instance=workflow)
        if form.is_valid():
            form.save()
            messages.success(request, 'Workflow atualizado com sucesso!')
            return redirect('automacao:editar_workflow', workflow_id=workflow.id)
    else:
        form = WorkflowForm(instance=workflow)
    
    # Ações do workflow
    acoes = workflow.acoes.all().order_by('ordem')
    
    context = {
        'workflow': workflow,
        'form': form,
        'acoes': acoes,
    }
    
    return render(request, 'automacao/workflows/editar.html', context)


@supervisor_or_admin_required
def adicionar_acao_workflow(request, workflow_id):
    """
    Adiciona uma nova ação ao workflow.
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    if request.method == 'POST':
        form = AcaoWorkflowForm(request.POST)
        if form.is_valid():
            acao = form.save(commit=False)
            acao.workflow = workflow
            # Definir ordem automaticamente
            ultima_ordem = workflow.acoes.aggregate(
                max_ordem=models.Max('ordem')
            )['max_ordem'] or 0
            acao.ordem = ultima_ordem + 1
            acao.save()
            
            messages.success(request, 'Ação adicionada ao workflow!')
            return redirect('automacao:editar_workflow', workflow_id=workflow.id)
    else:
        form = AcaoWorkflowForm()
    
    return render(request, 'automacao/workflows/adicionar_acao.html', {
        'workflow': workflow,
        'form': form,
    })


@supervisor_or_admin_required
def lista_campanhas(request):
    """
    Lista todas as campanhas de nutrição.
    """
    campanhas = CampanhaNutricao.objects.all().order_by('-data_criacao')
    
    # Filtros
    search_term = request.GET.get('search', '')
    if search_term:
        campanhas = campanhas.filter(
            Q(nome__icontains=search_term) |
            Q(descricao__icontains=search_term)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        campanhas = campanhas.filter(status=status_filter)
    
    # Adicionar estatísticas
    campanhas = campanhas.annotate(
        total_participantes=Count('participacaocampanha'),
        participantes_ativos=Count(
            'participacaocampanha',
            filter=Q(participacaocampanha__status='ativa')
        )
    )
      # Paginação
    paginator = Paginator(campanhas, 20)
    page = request.GET.get('page')
    campanhas = paginator.get_page(page)
    
    context = {
        'campanhas': campanhas,
        'status_choices': CampanhaNutricao.STATUS_CHOICES,
        'search_term': search_term,
        'status_filter': status_filter,
    }
    
    return render(request, 'automacao/campanha_list.html', context)


@supervisor_or_admin_required
def criar_campanha(request):
    """
    Cria uma nova campanha de nutrição.
    """
    if request.method == 'POST':
        form = CampanhaNutricaoForm(request.POST)
        if form.is_valid():
            campanha = form.save(commit=False)
            campanha.criado_por = request.user
            campanha.save()
            
            messages.success(request, f'Campanha "{campanha.nome}" criada com sucesso!')
            return redirect('automacao:editar_campanha', campanha_id=campanha.id)
    else:
        form = CampanhaNutricaoForm()
    
    return render(request, 'automacao/campanhas/criar.html', {'form': form})


@supervisor_or_admin_required
def editar_campanha(request, campanha_id):
    """
    Edita uma campanha existente e suas etapas.
    """
    campanha = get_object_or_404(CampanhaNutricao, id=campanha_id)
    
    if request.method == 'POST':
        form = CampanhaNutricaoForm(request.POST, instance=campanha)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campanha atualizada com sucesso!')
            return redirect('automacao:editar_campanha', campanha_id=campanha.id)
    else:
        form = CampanhaNutricaoForm(instance=campanha)
    
    # Etapas da campanha
    etapas = campanha.etapas.all().order_by('ordem')
    
    # Participantes
    participantes = campanha.participacaocampanha_set.select_related('lead').order_by('-data_entrada')[:10]
    
    context = {
        'campanha': campanha,
        'form': form,
        'etapas': etapas,
        'participantes': participantes,
    }
    
    return render(request, 'automacao/campanhas/editar.html', context)


@supervisor_or_admin_required
def lead_scoring_dashboard(request):
    """
    Dashboard do sistema de lead scoring.
    """
    # Estatísticas de score
    total_leads_com_score = LeadScore.objects.count()
    score_medio = LeadScore.objects.aggregate(Avg('pontuacao_total'))['pontuacao_total__avg'] or 0
    
    # Distribuição por classificação
    distribuicao = LeadScore.objects.values('classificacao').annotate(
        count=Count('id')
    ).order_by('classificacao')
    
    # Top leads por score
    top_leads = LeadScore.objects.select_related('lead').order_by('-pontuacao_total')[:20]
    
    # Leads que precisam de atenção (score baixo há muito tempo)
    leads_atencao = LeadScore.objects.filter(
        classificacao='frio',
        ultima_atualizacao__lt=timezone.now() - timedelta(days=7)
    ).select_related('lead')[:10]
    
    context = {
        'total_leads_com_score': total_leads_com_score,
        'score_medio': round(score_medio, 1),
        'distribuicao': distribuicao,
        'top_leads': top_leads,
        'leads_atencao': leads_atencao,
    }
    
    return render(request, 'automacao/lead_scoring_list.html', context)


@supervisor_or_admin_required
def recalcular_scores(request):
    """
    Recalcula os scores de todos os leads.
    """
    if request.method == 'POST':
        leads = Lead.objects.all()
        contador = 0
        
        for lead in leads:
            LeadScoringService.calcular_score_lead(lead)
            contador += 1
        
        messages.success(request, f'Scores recalculados para {contador} leads!')
        return redirect('automacao:lead_scoring_dashboard')
    
    return render(request, 'automacao/scoring/recalcular.html')


@login_required
def historico_automacao(request):
    """
    Exibe o histórico de ações de automação.
    """
    historico = HistoricoAutomacao.objects.select_related(
        'lead', 'workflow', 'campanha', 'gatilho'
    ).order_by('-data_execucao')
    
    # Filtros
    tipo_filter = request.GET.get('tipo', '')
    if tipo_filter:
        historico = historico.filter(tipo=tipo_filter)
    
    sucesso_filter = request.GET.get('sucesso', '')
    if sucesso_filter:
        historico = historico.filter(sucesso=sucesso_filter == 'true')
    
    lead_filter = request.GET.get('lead', '')
    if lead_filter:
        historico = historico.filter(lead__nome__icontains=lead_filter)
    
    # Paginação
    paginator = Paginator(historico, 50)
    page = request.GET.get('page')
    historico = paginator.get_page(page)
    
    context = {
        'historico': historico,
        'tipo_choices': HistoricoAutomacao.TIPO_CHOICES,
        'tipo_filter': tipo_filter,
        'sucesso_filter': sucesso_filter,
        'lead_filter': lead_filter,
    }
    
    return render(request, 'automacao/historico.html', context)


@supervisor_or_admin_required
def executar_automacao(request):
    """
    Executa manualmente o processamento de automação.
    """
    try:
        # Verificar se é uma execução forçada
        force = request.GET.get('force', 'false').lower() == 'true'
        
        # Chamar o comando de processamento
        call_command('processar_automacao', force=force)
        
        messages.success(
            request, 
            'Processamento de automação executado com sucesso! '
            'Verifique o histórico para mais detalhes.'
        )
    except Exception as e:
        messages.error(
            request, 
            f'Erro ao executar processamento de automação: {str(e)}'
        )
        
    return redirect('automacao:dashboard')


# APIs AJAX
@supervisor_or_admin_required
def api_executar_workflow(request, workflow_id):
    """
    API para executar um workflow manualmente em leads selecionados.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    workflow = get_object_or_404(Workflow, id=workflow_id)
    lead_ids = request.POST.getlist('lead_ids[]')
    
    if not lead_ids:
        return JsonResponse({'error': 'Nenhum lead selecionado'}, status=400)
    
    execucoes_criadas = 0
    for lead_id in lead_ids:
        try:
            lead = Lead.objects.get(id=lead_id)
            WorkflowService.executar_workflow(workflow, lead)
            execucoes_criadas += 1
        except Lead.DoesNotExist:
            continue
    
    return JsonResponse({
        'success': True,
        'message': f'Workflow executado para {execucoes_criadas} leads'
    })


@supervisor_or_admin_required
def api_adicionar_leads_campanha(request, campanha_id):
    """
    API para adicionar leads a uma campanha.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    campanha = get_object_or_404(CampanhaNutricao, id=campanha_id)
    lead_ids = request.POST.getlist('lead_ids[]')
    
    if not lead_ids:
        return JsonResponse({'error': 'Nenhum lead selecionado'}, status=400)
    
    adicionados = 0
    for lead_id in lead_ids:
        try:
            lead = Lead.objects.get(id=lead_id)
            participacao, created = ParticipacaoCampanha.objects.get_or_create(
                campanha=campanha,
                lead=lead
            )
            if created:
                adicionados += 1
        except Lead.DoesNotExist:
            continue
    
    return JsonResponse({
        'success': True,
        'message': f'{adicionados} leads adicionados à campanha'
    })


@login_required
def api_score_lead(request, lead_id):
    """
    API para obter ou recalcular o score de um lead específico.
    """
    lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        # Recalcular score
        pontuacao = LeadScoringService.calcular_score_lead(lead)
        return JsonResponse({
            'success': True,
            'pontuacao': pontuacao,
            'message': 'Score recalculado com sucesso'
        })
    
    # Retornar score atual
    try:
        score = lead.score
        return JsonResponse({
            'pontuacao_total': score.pontuacao_total,
            'classificacao': score.classificacao,
            'pontos_demograficos': score.pontos_demograficos,
            'pontos_comportamentais': score.pontos_comportamentais,
            'pontos_engajamento': score.pontos_engajamento,
            'pontos_interesse': score.pontos_interesse,
            'ultima_atualizacao': score.ultima_atualizacao.isoformat()
        })
    except LeadScore.DoesNotExist:
        return JsonResponse({
            'pontuacao_total': 0,
            'classificacao': 'frio',
            'pontos_demograficos': 0,
            'pontos_comportamentais': 0,
            'pontos_engajamento': 0,
            'pontos_interesse': 0,
            'ultima_atualizacao': None
        })


@login_required
@supervisor_or_admin_required
def lista_gatilhos(request):
    """
    Lista todos os gatilhos automáticos.
    """
    gatilhos = GatilhoAutomatico.objects.all().order_by('-data_criacao')
    
    # Filtros
    search_term = request.GET.get('search', '')
    if search_term:
        gatilhos = gatilhos.filter(
            Q(nome__icontains=search_term) |
            Q(descricao__icontains=search_term)
        )
    
    evento_filter = request.GET.get('evento', '')
    if evento_filter:
        gatilhos = gatilhos.filter(evento=evento_filter)
    
    ativo_filter = request.GET.get('ativo', '')
    if ativo_filter:
        gatilhos = gatilhos.filter(ativo=ativo_filter == 'true')
    
    # Paginação
    paginator = Paginator(gatilhos, 20)
    page = request.GET.get('page')
    gatilhos = paginator.get_page(page)
    
    context = {
        'gatilhos': gatilhos,
        'evento_choices': GatilhoAutomatico.EVENTO_CHOICES,
        'search_term': search_term,
        'evento_filter': evento_filter,
        'ativo_filter': ativo_filter,
    }
    
    return render(request, 'automacao/gatilho_list.html', context)


@login_required
@supervisor_or_admin_required
def criar_gatilho(request):
    """
    Cria um novo gatilho automático.
    """
    if request.method == 'POST':
        form = GatilhoAutomaticoForm(request.POST)
        if form.is_valid():
            gatilho = form.save(commit=False)
            gatilho.criado_por = request.user
            gatilho.save()
            
            messages.success(request, f'Gatilho "{gatilho.nome}" criado com sucesso!')
            return redirect('automacao:gatilho_list')
    else:
        form = GatilhoAutomaticoForm()
    
    return render(request, 'automacao/gatilho_form.html', {
        'form': form,
        'title': 'Criar Gatilho',
        'action': 'Criar'
    })


@login_required
@supervisor_or_admin_required
def editar_gatilho(request, gatilho_id):
    """
    Edita um gatilho automático existente.
    """
    gatilho = get_object_or_404(GatilhoAutomatico, id=gatilho_id)
    
    if request.method == 'POST':
        form = GatilhoAutomaticoForm(request.POST, instance=gatilho)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gatilho atualizado com sucesso!')
            return redirect('automacao:gatilho_list')
    else:
        form = GatilhoAutomaticoForm(instance=gatilho)
    
    context = {
        'form': form,
        'gatilho': gatilho,
        'title': 'Editar Gatilho',
        'action': 'Salvar'
    }
    
    return render(request, 'automacao/gatilho_form.html', context)


@login_required
@supervisor_or_admin_required
def listar_execucoes(request):
    """Lista as execuções de workflows."""
    execucoes = ExecucaoWorkflow.objects.all().order_by('-data_inicio')
    
    # Filtragem por status
    status_filter = request.GET.get('status')
    if status_filter:
        execucoes = execucoes.filter(status=status_filter)
    
    # Filtragem por período
    periodo = request.GET.get('periodo', 'todos')
    if periodo == 'hoje':
        execucoes = execucoes.filter(data_inicio__date=timezone.now().date())
    elif periodo == 'semana':
        execucoes = execucoes.filter(data_inicio__gte=timezone.now() - timedelta(days=7))
    elif periodo == 'mes':
        execucoes = execucoes.filter(data_inicio__gte=timezone.now() - timedelta(days=30))
    
    # Paginação
    paginator = Paginator(execucoes, 20)
    page_number = request.GET.get('page', 1)
    execucoes_paginadas = paginator.get_page(page_number)
    
    # Estatísticas
    total_execucoes = ExecucaoWorkflow.objects.count()
    execucoes_sucesso = ExecucaoWorkflow.objects.filter(status='concluido').count()
    execucoes_erro = ExecucaoWorkflow.objects.filter(status='erro').count()
    
    # Taxa de sucesso
    taxa_sucesso = 0
    if total_execucoes > 0:
        taxa_sucesso = (execucoes_sucesso / total_execucoes) * 100
    
    context = {
        'execucoes': execucoes_paginadas,
        'total_execucoes': total_execucoes,
        'execucoes_sucesso': execucoes_sucesso,
        'execucoes_erro': execucoes_erro,
        'taxa_sucesso': round(taxa_sucesso, 1),
        'status_filter': status_filter,
        'periodo': periodo,
    }
    
    return render(request, 'automacao/execucao_list.html', context)


@login_required
@supervisor_or_admin_required
def toggle_gatilho(request, gatilho_id):
    """Toggle the active status of a gatilho via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    gatilho = get_object_or_404(GatilhoAutomatico, id=gatilho_id)
    gatilho.ativo = not gatilho.ativo
    gatilho.save()
    
    return JsonResponse({
        'success': True,
        'ativo': gatilho.ativo,
        'message': f'Gatilho {"ativado" if gatilho.ativo else "desativado"} com sucesso!'
    })
