"""
Views consolidadas para gestão de leads.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from apps.common.mixins import supervisor_or_admin_required
from apps.common.utils import export_to_csv
from apps.leads.models_consolidated import Lead, TemplateComunitacao, HistoricoContato
from apps.leads.forms_consolidated import (
    LeadForm, QuickLeadForm, LeadFilterForm, 
    AdvancedSearchForm, TemplateForm, ContatoForm
)


@login_required
def lead_list(request):
    """Listagem de leads com filtros e paginação."""
    filter_form = LeadFilterForm(request.GET)
    advanced_search_form = AdvancedSearchForm(request.GET)
    
    # Base queryset
    queryset = Lead.objects.all()
    
    # Aplicar filtros
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        if data.get('busca'):
            search_term = data['busca']
            queryset = queryset.filter(
                Q(nome__icontains=search_term) |
                Q(empresa__icontains=search_term) |
                Q(telefone__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(whatsapp__icontains=search_term)
            )
        
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])
        
        if data.get('interesse'):
            queryset = queryset.filter(interesse=data['interesse'])
        
        if data.get('prioridade'):
            queryset = queryset.filter(prioridade=data['prioridade'])
        
        if data.get('fonte'):
            queryset = queryset.filter(fonte=data['fonte'])
    
    # Busca avançada
    if advanced_search_form.is_valid():
        data = advanced_search_form.cleaned_data
        campo = data.get('campo_busca')
        valor = data.get('valor_busca')
        
        if campo and valor:
            if campo == 'nome':
                queryset = queryset.filter(nome__icontains=valor)
            elif campo == 'telefone':
                queryset = queryset.filter(
                    Q(telefone__icontains=valor) | Q(whatsapp__icontains=valor)
                )
            elif campo == 'email':
                queryset = queryset.filter(email__icontains=valor)
            elif campo == 'empresa':
                queryset = queryset.filter(empresa__icontains=valor)
    
    # Paginação
    page_size = int(request.GET.get('per_page', 20))
    paginator = Paginator(queryset, page_size)
    page = request.GET.get('page', 1)
    
    try:
        leads = paginator.page(page)
    except PageNotAnInteger:
        leads = paginator.page(1)
    except EmptyPage:
        leads = paginator.page(paginator.num_pages)
    
    context = {
        'leads': leads,
        'filter_form': filter_form,
        'advanced_search_form': advanced_search_form,
        'total_leads': queryset.count(),
        'page_size': page_size,
    }
    
    return render(request, 'leads/list.html', context)


@login_required
def lead_create(request):
    """Criar novo lead."""
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.responsavel = request.user
            lead.save()
            
            messages.success(request, f'Lead {lead.nome} criado com sucesso!')
            next_url = request.POST.get('next', 'leads:list')
            return redirect(next_url)
    else:
        form = LeadForm()
    
    return render(request, 'leads/form.html', {
        'form': form,
        'title': 'Novo Lead',
        'action': 'Criar'
    })


@login_required
def lead_create_quick(request):
    """Criar lead rapidamente."""
    if request.method == 'POST':
        form = QuickLeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.responsavel = request.user
            lead.save()
            
            messages.success(request, f'Lead {lead.nome} criado com sucesso!')
            next_url = request.POST.get('next', 'leads:list')
            return redirect(next_url)
    else:
        form = QuickLeadForm()
    
    return render(request, 'leads/quick_form.html', {
        'form': form,
        'title': 'Cadastro Rápido de Lead'
    })


@login_required
def lead_detail(request, lead_id):
    """Detalhes do lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    contatos = lead.historico_contatos.all()[:10]  # Últimos 10 contatos
    
    context = {
        'lead': lead,
        'contatos': contatos,
    }
    
    return render(request, 'leads/detail.html', context)


@login_required
def lead_edit(request, lead_id):
    """Editar lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lead {lead.nome} atualizado com sucesso!')
            return redirect('leads:detail', lead_id=lead.id)
    else:
        form = LeadForm(instance=lead)
    
    return render(request, 'leads/form.html', {
        'form': form,
        'lead': lead,
        'title': f'Editar Lead: {lead.nome}',
        'action': 'Atualizar'
    })


@login_required
def lead_delete(request, lead_id):
    """Deletar lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        nome = lead.nome
        lead.delete()
        messages.success(request, f'Lead {nome} removido com sucesso!')
        return redirect('leads:list')
    
    return render(request, 'leads/confirm_delete.html', {'lead': lead})


@login_required
def lead_contact(request, lead_id):
    """Registrar contato com lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            contato = form.save(commit=False)
            contato.lead = lead
            contato.usuario = request.user
            contato.save()
            
            # Atualizar data do último contato
            lead.data_ultimo_contato = timezone.now()
            if lead.status == 'novo':
                lead.status = 'contatado'
            lead.save()
            
            messages.success(request, 'Contato registrado com sucesso!')
            return redirect('leads:detail', lead_id=lead.id)
    else:
        form = ContatoForm()
    
    context = {
        'form': form,
        'lead': lead,
        'title': f'Registrar Contato - {lead.nome}'
    }
    
    return render(request, 'leads/contact_form.html', context)


@supervisor_or_admin_required
def lead_export(request):
    """Exportar leads para CSV."""
    queryset = Lead.objects.all()
    
    # Aplicar mesmos filtros da listagem se necessário
    filter_form = LeadFilterForm(request.GET)
    if filter_form.is_valid():
        # Aplicar filtros...
        pass
    
    fields_mapping = {
        'nome': 'Nome',
        'empresa': 'Empresa',
        'telefone': 'Telefone',
        'whatsapp': 'WhatsApp',
        'email': 'E-mail',
        'interesse': 'Interesse',
        'valor_interesse': 'Valor de Interesse',
        'status': 'Status',
        'fonte': 'Fonte',
        'prioridade': 'Prioridade',
        'data_criacao': 'Data de Criação',
        'responsavel__username': 'Responsável',
    }
    
    filename = f'leads_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return export_to_csv(queryset, filename, fields_mapping)


# API Views
@login_required
@require_http_methods(["GET"])
def lead_api_list(request):
    """API para listagem de leads (JSON)."""
    queryset = Lead.objects.all()
    
    # Filtros
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
    
    search = request.GET.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(nome__icontains=search) |
            Q(empresa__icontains=search) |
            Q(telefone__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Paginação
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    paginator = Paginator(queryset, page_size)
    
    try:
        leads_page = paginator.page(page)
    except PageNotAnInteger:
        leads_page = paginator.page(1)
    except EmptyPage:
        leads_page = paginator.page(paginator.num_pages)
    
    # Serializar dados
    leads_data = []
    for lead in leads_page:
        leads_data.append({
            'id': lead.id,
            'nome': lead.nome,
            'empresa': lead.empresa or '',
            'telefone': lead.telefone or '',
            'whatsapp': lead.whatsapp or '',
            'email': lead.email or '',
            'status': lead.status,
            'status_display': lead.get_status_display(),
            'interesse': lead.interesse,
            'interesse_display': lead.get_interesse_display(),
            'valor_interesse': float(lead.valor_interesse) if lead.valor_interesse else None,
            'prioridade': lead.prioridade,
            'prioridade_display': lead.get_prioridade_display(),
            'data_criacao': lead.data_criacao.isoformat(),
            'data_ultimo_contato': lead.data_ultimo_contato.isoformat() if lead.data_ultimo_contato else None,
        })
    
    response_data = {
        'leads': leads_data,
        'pagination': {
            'current_page': leads_page.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': leads_page.has_next(),
            'has_previous': leads_page.has_previous(),
        }
    }
    
    return JsonResponse(response_data)


@login_required
@require_http_methods(["GET"])
def template_content_api(request):
    """API para obter conteúdo de template."""
    template_id = request.GET.get('template_id')
    
    if not template_id:
        return JsonResponse({'error': 'Template ID é obrigatório'}, status=400)
    
    try:
        template = TemplateComunitacao.objects.get(id=template_id, ativo=True)
        return JsonResponse({
            'assunto': template.assunto or '',
            'conteudo': template.conteudo,
        })
    except TemplateComunitacao.DoesNotExist:
        return JsonResponse({'error': 'Template não encontrado'}, status=404)
