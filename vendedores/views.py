from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import logout

from leads.models import Lead
from .models import TentativaContato
from .forms import TentativaContatoForm


@login_required
def dashboard_vendedor(request):
    """Dashboard do vendedor com resumo e leads disponíveis."""
    vendedor = request.user
    
    # Busca leads que não foram contatadas nos últimos 3 dias pelo usuário atual
    leads_disponiveis = []
    todas_leads = Lead.objects.filter(status__in=['novo', 'contatado', 'qualificado'])
    
    for lead in todas_leads:
        if TentativaContato.pode_contatar(lead, vendedor):
            # Verifica se a lead foi contatada recentemente por outro vendedor
            lead.contatada_recentemente = TentativaContato.foi_contatado_recentemente(lead)
            
            # Se a lead foi contatada por alguém e o usuário não é um admin,
            # verifica se o vendedor atual já contatou esta lead antes
            if lead.contatada_recentemente and not request.user.is_staff:
                # Apenas mostra a lead se o próprio vendedor já tentou contato com ela antes
                if TentativaContato.objects.filter(lead=lead, vendedor=vendedor).exists():
                    leads_disponiveis.append(lead)
            else:
                # Lead não foi contatada recentemente ou usuário é admin
                leads_disponiveis.append(lead)
    
    # Estatísticas de contatos
    contatos_hoje = TentativaContato.objects.filter(
        vendedor=vendedor,
        data_hora__date=timezone.now().date()
    ).count()
    
    contatos_semana = TentativaContato.objects.filter(
        vendedor=vendedor,
        data_hora__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    contatos_sucesso = TentativaContato.objects.filter(
        vendedor=vendedor,
        resultado='sucesso'
    ).count()
    
    context = {
        'leads_disponiveis': leads_disponiveis,
        'contatos_hoje': contatos_hoje,
        'contatos_semana': contatos_semana,
        'contatos_sucesso': contatos_sucesso,
    }
    
    return render(request, 'vendedores/dashboard.html', context)


@login_required
def registrar_contato(request, lead_id):
    """Permite ao vendedor registrar uma tentativa de contato com uma lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    vendedor = request.user
    
    # Verifica se o vendedor pode contatar esta lead
    if not TentativaContato.pode_contatar(lead, vendedor):
        messages.error(request, 'Você já contatou este lead nos últimos 3 dias.')
        return redirect('dashboard_vendedor')
    
    if request.method == 'POST':
        form = TentativaContatoForm(request.POST)
        if form.is_valid():
            tentativa = form.save(commit=False)
            tentativa.lead = lead
            tentativa.vendedor = vendedor
            tentativa.save()
            
            # Atualiza o status do lead se necessário
            if lead.status == 'novo':
                lead.status = 'contatado'
                lead.data_ultimo_contato = timezone.now()
                lead.save()
            
            messages.success(request, f'Contato com {lead.nome} registrado com sucesso!')
            return redirect('dashboard_vendedor')
    else:
        form = TentativaContatoForm()
    
    return render(request, 'vendedores/registrar_contato.html', {
        'form': form,
        'lead': lead,
    })


@login_required
def historico_contatos(request):
    """Exibe o histórico de contatos feitos pelo vendedor."""
    vendedor = request.user
    contatos = TentativaContato.objects.filter(vendedor=vendedor).order_by('-data_hora')
    
    return render(request, 'vendedores/historico_contatos.html', {
        'contatos': contatos,
    })


@login_required
def detalhes_lead(request, lead_id):
    """Exibe os detalhes de uma lead e seu histórico de contatos."""
    lead = get_object_or_404(Lead, id=lead_id)
    vendedor = request.user
    
    # Verifica se o vendedor pode contatar esta lead
    pode_contatar = TentativaContato.pode_contatar(lead, vendedor)
    
    # Verificar se a lead já foi contatada por alguém
    foi_contatado = TentativaContato.foi_contatado_recentemente(lead)
    
    # Se o usuário não é staff (admin) e a lead já foi contatada por outro vendedor, 
    # apenas exibimos os contatos feitos pelo próprio vendedor
    if not request.user.is_staff:
        contatos = TentativaContato.objects.filter(lead=lead, vendedor=vendedor).order_by('-data_hora')
    else:
        # Para admins/staff, mostrar todos os contatos
        contatos = TentativaContato.objects.filter(lead=lead).order_by('-data_hora')
    
    return render(request, 'vendedores/detalhes_lead.html', {
        'lead': lead,
        'contatos': contatos,
        'pode_contatar': pode_contatar,
        'foi_contatado': foi_contatado,
    })


@login_required
def logout_view(request):
    """Desconecta o usuário e redireciona para a página de login."""
    logout(request)
    return redirect('login')