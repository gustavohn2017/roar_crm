"""
Views consolidadas para a aplicação vendedores.
Inclui dashboard, gestão de contatos, eventos e notas.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import timedelta, date
import random

from apps.common.utils import export_to_csv
from apps.leads.models_consolidated import Lead
from .models import TentativaContato, Evento, Nota
from .forms_consolidated import (
    TentativaContatoForm, EventoForm, NotaForm, 
    QuickEventoForm, QuickNotaForm, EventoFilterForm, NotaFilterForm
)


@login_required
def dashboard_vendedor(request):
    """Dashboard principal do vendedor com estatísticas e leads disponíveis."""
    vendedor = request.user
    
    # Busca leads disponíveis para contato
    todas_leads = Lead.objects.filter(status__in=['novo', 'contatado', 'qualificado'])
    
    # Aplicar filtros da URL
    status_filter = request.GET.get('status_filter')
    interesse_filter = request.GET.get('interesse_filter')
    prioridade_filter = request.GET.get('prioridade_filter')
    
    if status_filter:
        todas_leads = todas_leads.filter(status=status_filter)
    if interesse_filter:
        todas_leads = todas_leads.filter(interesse=interesse_filter)
    if prioridade_filter:
        todas_leads = todas_leads.filter(prioridade=prioridade_filter)
    
    # Verificar quais leads estão disponíveis para contato
    leads_disponiveis = []
    for lead in todas_leads:
        if TentativaContato.pode_contatar(lead, vendedor):
            lead.contatada_recentemente = TentativaContato.foi_contatado_recentemente(lead)
            
            ultima_tentativa = TentativaContato.objects.filter(lead=lead).order_by('-data_hora').first()
            lead.data_ultimo_contato = ultima_tentativa.data_hora if ultima_tentativa else None
            
            # Regras de visibilidade (simplificadas)
            leads_disponiveis.append(lead)
    
    # Estatísticas do vendedor
    stats = _get_vendedor_stats(vendedor)
    
    # Próximos eventos e notas
    proximos_eventos = Evento.proximos_eventos(vendedor, dias=7)[:5]
    notas_pendentes = Nota.objects.filter(
        vendedor=vendedor, concluido=False
    ).order_by('-prioridade', '-data_criacao')[:5]
    
    # Atividades recentes
    atividades_recentes = TentativaContato.objects.filter(
        vendedor=vendedor
    ).order_by('-data_hora')[:10]
    
    # Leads recentes
    leads_recentes = Lead.objects.all().order_by('-data_criacao')[:5]
    
    # Dados para automação (se disponível)
    automacao_stats = _get_automacao_stats()
    
    context = {
        'leads_disponiveis': leads_disponiveis,
        'proximos_eventos': proximos_eventos,
        'notas_pendentes': notas_pendentes,
        'atividades_recentes': atividades_recentes,
        'leads_recentes': leads_recentes,
        'random_number': random.randint(10000, 99999),
        **stats,
        **automacao_stats,
    }
    
    return render(request, 'vendedores/dashboard.html', context)


def _get_vendedor_stats(vendedor):
    """Calcula estatísticas do vendedor."""
    hoje = timezone.now().date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)
    
    return {
        'contatos_hoje': TentativaContato.objects.filter(
            vendedor=vendedor, data_hora__date=hoje
        ).count(),
        'contatos_semana': TentativaContato.objects.filter(
            vendedor=vendedor, data_hora__date__gte=inicio_semana
        ).count(),
        'contatos_sucesso': TentativaContato.objects.filter(
            vendedor=vendedor, resultado='sucesso'
        ).count(),
        'reunioes_hoje': Evento.objects.filter(
            vendedor=vendedor, data=hoje, concluido=False
        ).count(),
        'vendas_mes': Lead.objects.filter(
            status='fechado',
            data_modificacao__gte=inicio_mes
        ).count(),
        'taxa_conversao': _calcular_taxa_conversao(),
    }


def _calcular_taxa_conversao():
    """Calcula taxa de conversão geral."""
    total_leads = Lead.objects.count()
    if total_leads > 0:
        leads_fechados = Lead.objects.filter(status='fechado').count()
        return round((leads_fechados / total_leads) * 100, 1)
    return 0


def _get_automacao_stats():
    """Obtém estatísticas de automação (se disponível)."""
    try:
        from automacao.models import Workflow, CampanhaNutricao, LeadScore, ParticipacaoCampanha
        
        campanhas_ativas = []
        for campanha in CampanhaNutricao.objects.filter(status='ativa')[:5]:
            participantes = ParticipacaoCampanha.objects.filter(campanha=campanha).count()
            concluidos = ParticipacaoCampanha.objects.filter(
                campanha=campanha, status='concluida'
            ).count()
            progresso = int((concluidos / participantes) * 100) if participantes > 0 else 0
            
            campanhas_ativas.append({
                'nome': campanha.nome,
                'participantes': participantes,
                'progresso': progresso
            })
        
        return {
            'total_workflows': Workflow.objects.filter(ativo=True).count(),
            'total_campanhas': CampanhaNutricao.objects.filter(status='ativa').count(),
            'leads_com_score': LeadScore.objects.count(),
            'leads_em_campanha': ParticipacaoCampanha.objects.filter(
                status='ativa'
            ).values('lead').distinct().count(),
            'top_leads_by_score': LeadScore.objects.order_by('-pontuacao_total')[:5],
            'campanhas_ativas': campanhas_ativas,
        }
    except ImportError:
        return {}


@login_required
def contatar_lead(request, lead_id):
    """Registra tentativa de contato com lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    vendedor = request.user
    
    # Verificar se pode contatar
    if not TentativaContato.pode_contatar(lead, vendedor):
        messages.error(request, 'Você já contatou esta lead recentemente. Aguarde 3 dias.')
        return redirect('vendedores:dashboard')
    
    if request.method == 'POST':
        form = TentativaContatoForm(request.POST)
        if form.is_valid():
            tentativa = form.save(commit=False)
            tentativa.lead = lead
            tentativa.vendedor = vendedor
            tentativa.save()
            
            # Atualizar status da lead se necessário
            if tentativa.resultado == 'sucesso' and lead.status == 'novo':
                lead.status = 'contatado'
                lead.save()
            
            messages.success(request, 'Tentativa de contato registrada com sucesso!')
            return redirect('vendedores:dashboard')
    else:
        form = TentativaContatoForm()
    
    return render(request, 'vendedores/contatar_lead.html', {
        'form': form,
        'lead': lead
    })


@login_required
def eventos_list(request):
    """Lista eventos do vendedor com filtros."""
    vendedor = request.user
    eventos = Evento.objects.filter(vendedor=vendedor)
    
    # Aplicar filtros
    filter_form = EventoFilterForm(request.GET)
    if filter_form.is_valid():
        periodo = filter_form.cleaned_data.get('periodo')
        status = filter_form.cleaned_data.get('status')
        tipo = filter_form.cleaned_data.get('tipo')
        
        if periodo and periodo != 'todos':
            hoje = date.today()
            if periodo == 'hoje':
                eventos = eventos.filter(data=hoje)
            elif periodo == 'semana':
                inicio_semana = hoje - timedelta(days=hoje.weekday())
                eventos = eventos.filter(data__gte=inicio_semana)
            elif periodo == 'mes':
                eventos = eventos.filter(data__month=hoje.month, data__year=hoje.year)
        
        if status and status != 'todos':
            if status == 'pendentes':
                eventos = eventos.filter(concluido=False)
            elif status == 'concluidos':
                eventos = eventos.filter(concluido=True)
            elif status == 'atrasados':
                eventos = eventos.filter(data__lt=date.today(), concluido=False)
        
        if tipo and tipo != 'todos':
            eventos = eventos.filter(tipo=tipo)
    
    # Paginação
    paginator = Paginator(eventos.order_by('data', 'hora'), 20)
    page = request.GET.get('page')
    eventos_page = paginator.get_page(page)
    
    return render(request, 'vendedores/eventos_list.html', {
        'eventos': eventos_page,
        'filter_form': filter_form,
    })


@login_required
def evento_create(request):
    """Cria novo evento."""
    if request.method == 'POST':
        form = EventoForm(request.POST, vendedor=request.user)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.vendedor = request.user
            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('vendedores:eventos_list')
    else:
        form = EventoForm(vendedor=request.user)
    
    return render(request, 'vendedores/evento_form.html', {'form': form})


@login_required
def evento_edit(request, evento_id):
    """Edita evento existente."""
    evento = get_object_or_404(Evento, id=evento_id, vendedor=request.user)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento, vendedor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('vendedores:eventos_list')
    else:
        form = EventoForm(instance=evento, vendedor=request.user)
    
    return render(request, 'vendedores/evento_form.html', {'form': form, 'evento': evento})


@login_required
def evento_toggle(request, evento_id):
    """Marca/desmarca evento como concluído."""
    evento = get_object_or_404(Evento, id=evento_id, vendedor=request.user)
    evento.concluido = not evento.concluido
    evento.save()
    
    status = 'concluído' if evento.concluido else 'reaberto'
    messages.success(request, f'Evento {status} com sucesso!')
    
    return redirect('vendedores:eventos_list')


@login_required
def notas_list(request):
    """Lista notas do vendedor com filtros."""
    vendedor = request.user
    notas = Nota.objects.filter(vendedor=vendedor)
    
    # Aplicar filtros
    filter_form = NotaFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        tipo = filter_form.cleaned_data.get('tipo')
        prioridade = filter_form.cleaned_data.get('prioridade')
        
        if status and status != 'todas':
            if status == 'ativas':
                notas = notas.filter(concluido=False)
            elif status == 'concluidas':
                notas = notas.filter(concluido=True)
        
        if tipo and tipo != 'todos':
            notas = notas.filter(tipo=tipo)
        
        if prioridade and prioridade != 'todas':
            notas = notas.filter(prioridade=int(prioridade))
    
    # Paginação
    paginator = Paginator(notas.order_by('-prioridade', '-data_criacao'), 20)
    page = request.GET.get('page')
    notas_page = paginator.get_page(page)
    
    return render(request, 'vendedores/notas_list.html', {
        'notas': notas_page,
        'filter_form': filter_form,
    })


@login_required
def nota_create(request):
    """Cria nova nota."""
    if request.method == 'POST':
        form = NotaForm(request.POST, vendedor=request.user)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.vendedor = request.user
            nota.save()
            messages.success(request, 'Nota criada com sucesso!')
            return redirect('vendedores:notas_list')
    else:
        form = NotaForm(vendedor=request.user)
    
    return render(request, 'vendedores/nota_form.html', {'form': form})


@login_required
def nota_edit(request, nota_id):
    """Edita nota existente."""
    nota = get_object_or_404(Nota, id=nota_id, vendedor=request.user)
    
    if request.method == 'POST':
        form = NotaForm(request.POST, instance=nota, vendedor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nota atualizada com sucesso!')
            return redirect('vendedores:notas_list')
    else:
        form = NotaForm(instance=nota, vendedor=request.user)
    
    return render(request, 'vendedores/nota_form.html', {'form': form, 'nota': nota})


@login_required
def nota_toggle(request, nota_id):
    """Marca/desmarca nota como concluída."""
    nota = get_object_or_404(Nota, id=nota_id, vendedor=request.user)
    nota.concluido = not nota.concluido
    nota.save()
    
    status = 'concluída' if nota.concluido else 'reaberta'
    messages.success(request, f'Nota {status} com sucesso!')
    
    return redirect('vendedores:notas_list')


# API Views para AJAX
@login_required
def api_quick_evento(request):
    """API para criação rápida de eventos via AJAX."""
    if request.method == 'POST':
        form = QuickEventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.vendedor = request.user
            evento.save()
            return JsonResponse({
                'success': True,
                'message': 'Evento criado com sucesso!',
                'evento': {
                    'id': evento.id,
                    'titulo': evento.titulo,
                    'data': evento.data.strftime('%d/%m/%Y'),
                    'hora': evento.hora.strftime('%H:%M'),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def api_quick_nota(request):
    """API para criação rápida de notas via AJAX."""
    if request.method == 'POST':
        form = QuickNotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.vendedor = request.user
            nota.save()
            return JsonResponse({
                'success': True,
                'message': 'Nota criada com sucesso!',
                'nota': {
                    'id': nota.id,
                    'titulo': nota.titulo,
                    'tipo': nota.get_tipo_display(),
                    'prioridade': nota.get_prioridade_display(),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def exportar_tentativas(request):
    """Exporta tentativas de contato para CSV."""
    tentativas = TentativaContato.objects.filter(vendedor=request.user)
    
    headers = ['Data', 'Lead', 'Resultado', 'Observações']
    data = []
    
    for tentativa in tentativas:
        data.append([
            tentativa.data_hora.strftime('%d/%m/%Y %H:%M'),
            tentativa.lead.nome,
            tentativa.get_resultado_display(),
            tentativa.observacoes or ''
        ])
    
    return export_to_csv(data, headers, 'tentativas_contato')
