"""
Arquivo consolidado de views para o app leads.
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
from leads.models import Lead, TemplateComunitacao, HistoricoContato
from leads.forms import (
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
    
    return render(request, 'leads/lista_leads.html', context)


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
            lead.save()
            
            messages.success(request, f'Contato registrado com sucesso!')
            return redirect('leads:detail', lead_id=lead.id)
    else:
        form = ContatoForm()
    
    return render(request, 'leads/contact_form.html', {
        'form': form,
        'lead': lead,
    })


@login_required
@supervisor_or_admin_required
def lead_export(request):
    """Exportar leads para CSV."""
    queryset = Lead.objects.all()
    
    # Aplicar os mesmos filtros da listagem
    filter_form = LeadFilterForm(request.GET)
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        if data.get('busca'):
            search_term = data['busca']
            queryset = queryset.filter(
                Q(nome__icontains=search_term) |
                Q(empresa__icontains=search_term) |
                Q(telefone__icontains=search_term) |
                Q(email__icontains=search_term)
            )
        
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])
        
        if data.get('interesse'):
            queryset = queryset.filter(interesse=data['interesse'])
        
        if data.get('prioridade'):
            queryset = queryset.filter(prioridade=data['prioridade'])
    
    # Configurar campos para exportação
    fields = [
        'nome', 'cpf_cnpj', 'email', 'telefone', 'whatsapp',
        'empresa', 'cargo', 
        'interesse', 'valor_interesse', 'prazo_desejado',
        'status', 'fonte', 'prioridade',
        'data_criacao', 'data_ultimo_contato'
    ]
    
    # Configurar cabeçalhos legíveis
    headers = {
        'nome': 'Nome',
        'cpf_cnpj': 'CPF/CNPJ',
        'email': 'E-mail',
        'telefone': 'Telefone',
        'whatsapp': 'WhatsApp',
        'empresa': 'Empresa',
        'cargo': 'Cargo',
        'interesse': 'Interesse',
        'valor_interesse': 'Valor de Interesse',
        'prazo_desejado': 'Prazo Desejado',
        'status': 'Status',
        'fonte': 'Fonte',
        'prioridade': 'Prioridade',
        'data_criacao': 'Data de Criação',
        'data_ultimo_contato': 'Último Contato'
    }
    
    # Usar helper para exportar
    return export_to_csv(queryset, 'leads_export', headers)


# Views para templates de comunicação
@login_required
def template_list(request):
    """Listar templates de comunicação."""
    templates = TemplateComunitacao.objects.all()
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'leads/templates/list.html', context)


@login_required
def template_create(request):
    """Criar novo template."""
    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.criado_por = request.user
            template.save()
            
            messages.success(request, f'Template {template.nome} criado com sucesso!')
            return redirect('leads:template_list')
    else:
        form = TemplateForm()
    
    return render(request, 'leads/templates/form.html', {
        'form': form,
        'title': 'Novo Template',
        'action': 'Criar'
    })


@login_required
def template_edit(request, template_id):
    """Editar template."""
    template = get_object_or_404(TemplateComunitacao, id=template_id)
    
    if request.method == 'POST':
        form = TemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, f'Template {template.nome} atualizado com sucesso!')
            return redirect('leads:template_list')
    else:
        form = TemplateForm(instance=template)
    
    return render(request, 'leads/templates/form.html', {
        'form': form,
        'template': template,
        'title': f'Editar Template: {template.nome}',
        'action': 'Atualizar'
    })


@login_required
def template_delete(request, template_id):
    """Deletar template."""
    template = get_object_or_404(TemplateComunitacao, id=template_id)
    
    if request.method == 'POST':
        nome = template.nome
        template.delete()
        messages.success(request, f'Template {nome} removido com sucesso!')
        return redirect('leads:template_list')
    
    return render(request, 'leads/templates/confirm_delete.html', {'template': template})
