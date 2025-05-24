from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Lead
from .forms import QuickLeadForm, LeadFilterForm, AdvancedSearchForm

@login_required
def cadastrar_lead(request):
    """Formulário de cadastro rápido de leads."""
    if request.method == 'POST':
        form = QuickLeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.responsavel = request.user
            lead.data_criacao = timezone.now()
            lead.save()
            
            messages.success(request, f'Lead {lead.nome} cadastrado com sucesso!')
            
            # Redireciona para diferentes lugares dependendo de onde o formulário foi enviado
            next_url = request.POST.get('next', 'vendedores:dashboard_vendedor')
            return redirect(next_url)
    else:
        form = QuickLeadForm()
        
    return render(request, 'leads/cadastrar_lead.html', {
        'form': form,
        'title': 'Cadastro Rápido de Lead',
    })

@login_required
def lista_leads(request):
    """Listagem de leads com filtros e paginação."""
    filter_form = LeadFilterForm(request.GET)
    advanced_search_form = AdvancedSearchForm(request.GET)
    
    # Filtros aplicados
    filters = Q()
    if request.GET.get('status'):
        filters &= Q(status=request.GET.get('status'))
    if request.GET.get('interesse'):
        filters &= Q(interesse=request.GET.get('interesse'))
    if request.GET.get('prioridade'):
        filters &= Q(prioridade=request.GET.get('prioridade'))
    if request.GET.get('busca'):
        search_term = request.GET.get('busca')
        search_filter = Q(nome__icontains=search_term) | Q(empresa__icontains=search_term) | Q(telefone__icontains=search_term) | Q(email__icontains=search_term) | Q(whatsapp__icontains=search_term)
        filters &= search_filter
    
    # Filtro avançado
    if request.GET.get('campo_busca') and request.GET.get('valor_busca'):
        campo = request.GET.get('campo_busca')
        valor = request.GET.get('valor_busca')
        
        # Construção dinâmica de filtro baseado no campo selecionado
        if campo == 'nome':
            filters &= Q(nome__icontains=valor)
        elif campo == 'telefone':
            filters &= Q(telefone__icontains=valor) | Q(whatsapp__icontains=valor)
        elif campo == 'email':
            filters &= Q(email__icontains=valor)
        elif campo == 'empresa':
            filters &= Q(empresa__icontains=valor)
    
    # Aplicar filtros
    leads = Lead.objects.filter(filters)
    
    # Configuração da paginação
    items_per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(leads, items_per_page)
    page = request.GET.get('page', 1)
    
    try:
        paginated_leads = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, mostrar a primeira página
        paginated_leads = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do alcance, mostrar a última página
        paginated_leads = paginator.page(paginator.num_pages)
    
    return render(request, 'leads/lista_leads.html', {
        'leads': paginated_leads,
        'filter_form': filter_form,
        'advanced_search_form': advanced_search_form,
        'total_leads': leads.count(),
        'items_per_page': items_per_page,
        'current_page': int(page),
    })

@login_required
def detalhes_lead(request, lead_id):
    """Detalhes de um lead específico."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Verificar se o usuário tem acesso a este lead
    # (implementar lógica de permissões conforme necessário)
    
    return render(request, 'leads/detalhes_lead.html', {
        'lead': lead,
    })

@login_required
def editar_lead(request, lead_id):
    """Editar informações de um lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        form = QuickLeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lead {lead.nome} atualizado com sucesso!')
            return redirect('detalhes_lead', lead_id=lead.id)
    else:
        form = QuickLeadForm(instance=lead)
    
    return render(request, 'leads/cadastrar_lead.html', {
        'form': form,
        'lead': lead,
        'title': f'Editar Lead: {lead.nome}',
    })
