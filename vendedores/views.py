# Note: App namespace changed from 'vendedores' to 'main' for better semantics
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import logout
from django import forms
from django.db.models import Q
import random
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime
from django.utils.timezone import make_aware

from leads.models import Lead
from .models import TentativaContato, Evento, Nota
from .forms import TentativaContatoForm


# Forms para eventos e notas
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descricao', 'data', 'hora', 'tipo', 'lead']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        vendedor = kwargs.pop('vendedor', None)
        super().__init__(*args, **kwargs)
        if vendedor:
            self.fields['lead'].queryset = Lead.objects.filter(status__in=['novo', 'contatado', 'qualificado']).order_by('nome')
        self.fields['lead'].required = False
        self.fields['lead'].empty_label = "Nenhum lead associado"


class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['titulo', 'conteudo', 'prioridade', 'tipo', 'lead']
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        vendedor = kwargs.pop('vendedor', None)
        super().__init__(*args, **kwargs)
        if vendedor:
            self.fields['lead'].queryset = Lead.objects.filter(status__in=['novo', 'contatado', 'qualificado']).order_by('nome')
        self.fields['lead'].required = False
        self.fields['lead'].empty_label = "Nenhum lead associado"
        
        # Definir choices para o campo tipo
        TIPO_CHOICES = [
            ('nota', 'Nota'),
            ('lembrete', 'Lembrete'),
        ]
        self.fields['tipo'].choices = TIPO_CHOICES
        self.fields['tipo'].initial = 'nota'


@login_required
def dashboard_vendedor(request):
    """Dashboard do vendedor com resumo e leads disponíveis."""
    vendedor = request.user
    
    # Busca leads que não foram contatadas nos últimos 3 dias pelo usuário atual
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
            # Verifica se a lead foi contatada recentemente por outro vendedor
            lead.contatada_recentemente = TentativaContato.foi_contatado_recentemente(lead)
            
            # Obter a data do último contato para exibição na interface
            ultima_tentativa = TentativaContato.objects.filter(lead=lead).order_by('-data_hora').first()
            lead.data_ultimo_contato = ultima_tentativa.data_hora if ultima_tentativa else None
            
            # Se a lead foi contatada por alguém e o usuário não é um admin ou supervisor,
            # verifica se o vendedor atual já contatou esta lead antes
            if lead.contatada_recentemente and not request.user.profile.has_role_or_higher('supervisor'):
                # Apenas mostra a lead se o próprio vendedor já tentou contato com ela antes
                if TentativaContato.objects.filter(lead=lead, vendedor=vendedor).exists():
                    leads_disponiveis.append(lead)
            else:
                # Lead não foi contatada recentemente ou usuário é admin
                leads_disponiveis.append(lead)
    
    # Buscar eventos próximos para mostrar no dashboard
    from datetime import date, timedelta
    from .models import Evento, Nota
    
    hoje = date.today()
    proximos_eventos = Evento.objects.filter(
        vendedor=vendedor,
        data__gte=hoje,
        data__lte=hoje + timedelta(days=7),  # Próximos 7 dias
        concluido=False
    ).order_by('data', 'hora')[:3]
      # Buscar notas pendentes para mostrar no dashboard
    notas_pendentes = Nota.objects.filter(
        vendedor=vendedor,
        concluido=False
    ).order_by('-prioridade')[:3]
    
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
    
    # Atividades recentes - últimas tentativas de contato
    atividades_recentes = TentativaContato.objects.all().order_by('-data_hora')[:10]
    
    # Note: App namespace changed from 'vendedores' to 'main' for better semantics
    # Leads recém adicionados
    leads_recentes = Lead.objects.all().order_by('-data_criacao')[:5]
      # Próximos eventos e lembretes para o dashboard
    eventos_proximos = Evento.proximos_eventos(vendedor, dias=7)[:5]
    lembretes_pendentes = Nota.lembretes_ativos(vendedor)[:5]
    
    # Adicionar um número aleatório para evitar cache de scripts
    from datetime import date
    random_number = random.randint(10000, 99999)
    
    # Estatísticas adicionais para o dashboard
    total_leads = Lead.objects.count()
    vendas_mes = Lead.objects.filter(
        status='fechado',
        data_modificacao__month=timezone.now().month,
        data_modificacao__year=timezone.now().year
    ).count()
    
    taxa_conversao = 0
    if total_leads > 0:
        leads_fechados = Lead.objects.filter(status='fechado').count()
        taxa_conversao = (leads_fechados / total_leads) * 100    # Contagem de reuniões para hoje
    hoje = date.today()
    reunioes_hoje = Evento.objects.filter(
        vendedor=vendedor,
        data=hoje,
        concluido=False
    ).count()
    
    # Dados para o widget de automação
    from automacao.models import Workflow, CampanhaNutricao, LeadScore, ParticipacaoCampanha

    # Total de workflows, campanhas e leads pontuados
    total_workflows = Workflow.objects.filter(ativo=True).count()
    total_campanhas = CampanhaNutricao.objects.filter(status='ativa').count()
    leads_com_score = LeadScore.objects.count()
    leads_em_campanha = ParticipacaoCampanha.objects.filter(status='ativa').values('lead').distinct().count()
    
    # Top leads por score
    top_leads_by_score = LeadScore.objects.order_by('-pontuacao_total')[:5]
    
    # Campanhas ativas com contagem de participantes
    campanhas_ativas = []
    for campanha in CampanhaNutricao.objects.filter(status='ativa')[:5]:
        participantes = ParticipacaoCampanha.objects.filter(campanha=campanha).count()
        progresso = 0
        if participantes > 0:
            concluidos = ParticipacaoCampanha.objects.filter(campanha=campanha, status='concluida').count()
            progresso = int((concluidos / participantes) * 100) if participantes > 0 else 0
        
        campanhas_ativas.append({
            'nome': campanha.nome,
            'participantes': participantes,
            'progresso': progresso
        })
    
    context = {
        'leads_disponiveis': leads_disponiveis,
        'contatos_hoje': contatos_hoje,
        'contatos_semana': contatos_semana,
        'contatos_sucesso': contatos_sucesso,
        'atividades_recentes': atividades_recentes,
        # Dados de automação para o widget
        'total_workflows': total_workflows,
        'total_campanhas': total_campanhas,
        'leads_com_score': leads_com_score,
        'leads_em_campanha': leads_em_campanha,
        'top_leads_by_score': top_leads_by_score,
        'campanhas_ativas': campanhas_ativas,
        'leads_recentes': leads_recentes,
        'proximos_eventos': proximos_eventos,
        'notas_pendentes': notas_pendentes,
        'eventos_proximos': eventos_proximos,
        'lembretes_pendentes': lembretes_pendentes,
        'status_filter': status_filter,
        'interesse_filter': interesse_filter,
        'prioridade_filter': prioridade_filter,
        'random_number': random_number,  # Para evitar cache
        'interesse_choices': Lead.INTEREST_CHOICES,
        'fonte_choices': Lead.SOURCE_CHOICES,
        'status_choices': Lead.STATUS_CHOICES,
        'total_leads': total_leads,
        'vendas_mes': vendas_mes,
        'taxa_conversao': taxa_conversao if isinstance(taxa_conversao, str) else f"{taxa_conversao:.1f}",  # Formatado para exibição
        'reunioes_hoje': reunioes_hoje,
        'hoje': hoje,
    }
      # Renderizar o template do dashboard novo
    return render(request, 'vendedores/dashboard_novo.html', context)


@login_required
def registrar_contato(request, lead_id):
    """Permite ao vendedor registrar uma tentativa de contato com uma lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    vendedor = request.user    # Verifica se o vendedor pode contatar esta lead
    if not TentativaContato.pode_contatar(lead, vendedor):
        messages.error(request, 'Você já contatou este lead nos últimos 3 dias.')
        return redirect('main:dashboard_principal')
    
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
            return redirect('vendedores:dashboard_vendedor')
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
      # Se o usuário não é supervisor ou admin e a lead já foi contatada por outro vendedor, 
    # apenas exibimos os contatos feitos pelo próprio vendedor
    if not request.user.profile.has_role_or_higher('supervisor'):
        contatos = TentativaContato.objects.filter(lead=lead, vendedor=vendedor).order_by('-data_hora')
    else:
        # Para supervisores e admins, mostrar todos os contatos
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

@login_required
def calendario_view(request):
    """Exibe o calendário de eventos e compromissos do vendedor."""
    vendedor = request.user
    
    from .models import Evento
    import calendar
    from datetime import date, datetime, timedelta
    
    # Configurar calendário para começar na segunda-feira (padrão brasileiro)
    calendar.setfirstweekday(calendar.MONDAY)
    
    # Obter mês e ano da query string ou usar o atual
    hoje = date.today()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))
    
    # Validar mês e ano
    if mes < 1: mes, ano = 12, ano-1
    if mes > 12: mes, ano = 1, ano+1
    
    # Criar calendário para o mês atual
    cal = calendar.monthcalendar(ano, mes)
    mes_nome = calendar.month_name[mes]
    
    # Buscar eventos do vendedor para o mês selecionado
    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)
    
    eventos = Evento.objects.filter(
        vendedor=vendedor,
        data__gte=primeiro_dia,
        data__lte=ultimo_dia
    ).order_by('data', 'hora')
    
    # Organizar eventos por dia
    eventos_por_dia = {}
    for evento in eventos:
        dia = evento.data.day
        if dia not in eventos_por_dia:
            eventos_por_dia[dia] = []
        eventos_por_dia[dia].append(evento)
    
    # Próximos eventos (independente do mês selecionado)
    proximos_eventos = Evento.objects.filter(
        vendedor=vendedor,
        data__gte=hoje,
        data__lte=hoje + timedelta(days=7)  # Próximos 7 dias
    ).order_by('data', 'hora')
    
    # Eventos atrasados não concluídos
    eventos_atrasados = Evento.objects.filter(
        vendedor=vendedor,
        data__lt=hoje,
        concluido=False
    ).order_by('data', 'hora')
    
    # Listar leads para relacionamento com eventos
    leads = Lead.objects.filter(status__in=['novo', 'contatado', 'qualificado']).order_by('nome')
    
    # Criar links para mês anterior e próximo
    mes_anterior = (mes - 1) if mes > 1 else 12
    ano_anterior = ano if mes > 1 else ano - 1
    
    mes_seguinte = (mes + 1) if mes < 12 else 1
    ano_seguinte = ano if mes < 12 else ano + 1
    
    context = {
        'eventos': eventos,
        'eventos_por_dia': eventos_por_dia,
        'proximos_eventos': proximos_eventos,
        'eventos_atrasados': eventos_atrasados,
        'leads': leads,
        'calendario': cal,
        'mes': mes,
        'mes_nome': mes_nome,
        'ano': ano,
        'hoje': hoje,
        'mes_anterior': mes_anterior,
        'ano_anterior': ano_anterior,
        'mes_seguinte': mes_seguinte,
        'ano_seguinte': ano_seguinte,
    }
    
    return render(request, 'vendedores/utils/calendario.html', context)

@login_required
def notas_view(request):
    """Exibe as notas e lembretes do vendedor."""
    vendedor = request.user
    
    # Aplicar filtros se existirem
    search_term = request.GET.get('search', '')
    priority_filter = request.GET.get('priority', '')
    status_filter = request.GET.get('status', '')
    
    # Buscar notas do vendedor com filtros
    notas = Nota.objects.filter(vendedor=vendedor)
    
    if search_term:
        notas = notas.filter(Q(titulo__icontains=search_term) | Q(conteudo__icontains=search_term))
    
    if priority_filter:
        notas = notas.filter(prioridade=priority_filter)
        
    if status_filter == 'pendente':
        notas = notas.filter(concluido=False)
    elif status_filter == 'concluido':
        notas = notas.filter(concluido=True)
    
    # Ordenar as notas
    notas = notas.order_by('-prioridade', '-data_criacao')
    
    # Separar notas entre pendentes e concluídas
    notas_pendentes = [nota for nota in notas if not nota.concluido]
    notas_concluidas = [nota for nota in notas if nota.concluido]
    
    # Separar lembretes (notas com data_lembrete definida)
    lembretes = [nota for nota in notas if nota.concluido is False and nota.tipo == 'lembrete']
    
    # Listar leads para relacionamento com notas
    leads = Lead.objects.filter(status__in=['novo', 'contatado', 'qualificado']).order_by('nome')
    
    context = {
        'notas': notas,
        'notas_pendentes': notas_pendentes,
        'notas_concluidas': notas_concluidas,
        'lembretes': lembretes,
        'leads': leads,
        'search_term': search_term,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'vendedores/utils/notas.html', context)

@login_required
def calculadoras_view(request):
    """Exibe as calculadoras de consórcio."""
    vendedor = request.user
    
    # Configurações das taxas de administração típicas por tipo de consórcio
    taxas_admin = {
        'auto': {'min': 10.0, 'default': 16.5, 'max': 20.0},
        'imovel': {'min': 10.0, 'default': 14.5, 'max': 20.0},
        'pesados': {'min': 12.0, 'default': 18.0, 'max': 22.0},
        'servicos': {'min': 11.0, 'default': 15.0, 'max': 19.0},
    }
    
    # Buscar leads para eventual associação com propostas geradas
    leads = Lead.objects.filter(status__in=['novo', 'contatado', 'qualificado']).order_by('nome')
    
    context = {
        'taxas_admin': taxas_admin,
        'leads': leads,
    }
    
    return render(request, 'vendedores/utils/calculadoras.html', context)


@login_required
def criar_evento(request):
    """Cria um novo evento no calendário."""
    if request.method == 'POST':
        form = EventoForm(request.POST, vendedor=request.user)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.vendedor = request.user
            evento.save()
            
            # Only add success message if not coming from management panel
            referrer = request.META.get('HTTP_REFERER', '')
            if '/gerencia/' not in referrer:
                messages.success(request, 'Evento criado com sucesso.')
            
            return redirect('main:calendario')
    else:
        # Pré-preencher data se fornecida na URL
        initial = {}
        if request.GET.get('data'):
            try:
                from datetime import datetime
                data = datetime.strptime(request.GET.get('data'), '%Y-%m-%d').date()
                initial['data'] = data
            except:
                pass
        form = EventoForm(vendedor=request.user, initial=initial)
    
    return render(request, 'vendedores/utils/evento_form.html', {
        'form': form, 
        'titulo': 'Criar novo evento',
        'action': 'criar'
    })


@login_required
def editar_evento(request, evento_id):
    """Edita um evento existente."""
    evento = get_object_or_404(Evento, id=evento_id, vendedor=request.user)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento, vendedor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso.')
            return redirect('main:calendario')
    else:
        form = EventoForm(instance=evento, vendedor=request.user)
    
    return render(request, 'vendedores/utils/evento_form.html', {
        'form': form,
        'titulo': 'Editar evento',
        'action': 'editar',
        'evento': evento
    })


@login_required
def excluir_evento(request, evento_id):
    """Exclui um evento."""
    evento = get_object_or_404(Evento, id=evento_id, vendedor=request.user)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso.')
        return redirect('main:calendario')
    
    return render(request, 'vendedores/utils/confirmar_exclusao.html', {
        'objeto': evento,
        'tipo': 'evento',
        'titulo': evento.titulo
    })


@login_required
def toggle_evento_concluido(request, evento_id):
    """Marca/desmarca um evento como concluído."""
    evento = get_object_or_404(Evento, id=evento_id, vendedor=request.user)
    evento.concluido = not evento.concluido
    evento.save()
    return redirect('main:calendario')


@login_required
def criar_nota(request):
    """Cria uma nova nota ou lembrete."""
    if request.method == 'POST':
        form = NotaForm(request.POST, vendedor=request.user)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.vendedor = request.user
            nota.save()
            messages.success(request, 'Nota criada com sucesso.')
            return redirect('main:notas')
    else:
        form = NotaForm(vendedor=request.user)
    
    return render(request, 'vendedores/utils/nota_form.html', {
        'form': form, 
        'titulo': 'Criar nova nota',
        'action': 'criar'
    })


@login_required
def editar_nota(request, nota_id):
    """Edita uma nota existente."""
    nota = get_object_or_404(Nota, id=nota_id, vendedor=request.user)
    
    if request.method == 'POST':
        form = NotaForm(request.POST, instance=nota, vendedor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nota atualizada com sucesso.')
            return redirect('main:notas')
    else:
        form = NotaForm(instance=nota, vendedor=request.user)
    
    return render(request, 'vendedores/utils/nota_form.html', {
        'form': form,
        'titulo': 'Editar nota',
        'action': 'editar',
        'nota': nota
    })


@login_required
def excluir_nota(request, nota_id):
    """Exclui uma nota."""
    nota = get_object_or_404(Nota, id=nota_id, vendedor=request.user)
    
    if request.method == 'POST':
        nota.delete()
        messages.success(request, 'Nota excluída com sucesso.')
        return redirect('main:notas')
    
    return render(request, 'vendedores/utils/confirmar_exclusao.html', {
        'objeto': nota,
        'tipo': 'nota',
        'titulo': nota.titulo
    })


@login_required
def toggle_nota_concluida(request, nota_id):
    """Marca/desmarca uma nota como concluída."""
    nota = get_object_or_404(Nota, id=nota_id, vendedor=request.user)
    nota.concluido = not nota.concluido
    nota.save()
    return redirect('main:notas')

@login_required
def gerar_proposta_pdf(request):
    """Gera um PDF com a proposta de consórcio calculada pelo usuário."""
    from django.http import HttpResponse
    import io
    import logging
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from datetime import datetime
    
    # Log para debug
    logger = logging.getLogger(__name__)
    
    # Obter dados da requisição POST
    if request.method == 'POST':
        # Registrar parâmetros recebidos para debug
        logger.info(f"Parâmetros recebidos: {request.POST}")
        tipo_consorcio = request.POST.get('tipo_consorcio')
        valor_credito = float(request.POST.get('valor_credito', 0))
        prazo = int(request.POST.get('prazo', 0))
        taxa_admin = float(request.POST.get('taxa_admin', 0))
        valor_parcela = float(request.POST.get('valor_parcela', 0))
        valor_total = float(request.POST.get('valor_total', 0))
        lead_id = request.POST.get('lead_id')
        
        # Buscar lead se especificado
        lead = None
        if lead_id and lead_id != '0':
            lead = Lead.objects.get(id=lead_id)
        
        # Criar um arquivo PDF em memória
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container para os elementos do PDF
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='TituloProposta', fontSize=16, alignment=TA_CENTER, textColor=colors.gold, spaceAfter=20))
        styles.add(ParagraphStyle(name='Subtitulo', fontSize=12, spaceAfter=10))
        styles.add(ParagraphStyle(name='Destaque', fontSize=14, textColor=colors.darkblue))
        
        # Título
        titulo_consorcio = ""
        if tipo_consorcio == 'auto':
            titulo_consorcio = "Proposta de Consórcio para Automóveis"
        elif tipo_consorcio == 'imovel':
            titulo_consorcio = "Proposta de Consórcio Imobiliário"
        elif tipo_consorcio == 'pesados':
            titulo_consorcio = "Proposta de Consórcio para Veículos Pesados"
        else:
            titulo_consorcio = "Proposta de Consórcio"
            
        titulo = Paragraph(titulo_consorcio, styles['TituloProposta'])
        elements.append(titulo)
        
        # Data da proposta
        data_atual = datetime.now().strftime("%d/%m/%Y")
        elements.append(Paragraph(f"Proposta gerada em: {data_atual}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Dados do cliente
        if lead:
            elements.append(Paragraph("Dados do Cliente:", styles['Subtitulo']))
            dados_cliente = [
                ["Nome:", lead.nome],
                ["Email:", lead.email],
                ["Telefone:", lead.telefone],
                ["Interesse:", lead.get_interesse_display()]
            ]
            t = Table(dados_cliente, colWidths=[100, 300])
            t.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.2*inch))
        
        # Dados da simulação
        elements.append(Paragraph("Detalhes da Simulação:", styles['Subtitulo']))
        dados_simulacao = [
            ["Valor do Crédito:", f"R$ {valor_credito:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Prazo do Plano:", f"{prazo} meses ({prazo//12} anos{' e '+str(prazo%12)+' meses' if prazo%12 else ''})"],
            ["Taxa de Administração:", f"{taxa_admin:.2f}%"],
            ["Valor da Parcela:", f"R$ {valor_parcela:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Valor Total do Plano:", f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ]
        t = Table(dados_simulacao, colWidths=[150, 250])
        t.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
            ('FONT', (1, 4), (1, 4), 'Helvetica-Bold'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3*inch))
        
        # Informações adicionais
        elements.append(Paragraph("Informações Importantes:", styles['Subtitulo']))
        elements.append(Paragraph("• A contemplação ocorre por meio de sorteio mensal ou lance, a partir da primeira assembleia.", styles['Normal']))
        elements.append(Paragraph("• O valor da parcela pode sofrer reajustes anuais conforme índices previstos em contrato.", styles['Normal']))
        elements.append(Paragraph("• Após a contemplação, o consorciado terá o crédito disponível para aquisição do bem.", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Contato do vendedor
        elements.append(Paragraph("Dados do Consultor:", styles['Subtitulo']))
        elements.append(Paragraph(f"Nome: {request.user.get_full_name()}", styles['Normal']))
        elements.append(Paragraph(f"Email: {request.user.email}", styles['Normal']))
        elements.append(Paragraph("Lions Consórcios - O seu caminho para conquistas!", styles['Destaque']))
        
        # Construir o PDF
        doc.build(elements)
        
        # Obter o PDF do buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Criar resposta HTTP com o PDF
        response = HttpResponse(content_type='application/pdf')
        
        # Nome do cliente ou "proposta" se não houver cliente
        nome_cliente = lead.nome.replace(' ', '_') if lead else "proposta"
        response['Content-Disposition'] = f'attachment; filename="consorcio_{tipo_consorcio}_{nome_cliente}.pdf"'
        
        # Escrever o PDF na resposta        response.write(pdf)
        return response
    
    return redirect('main:calculadoras')

@login_required
def funil_vendas_view(request):
    """Exibe o funil de vendas com leads em diferentes estágios."""
    vendedor = request.user
    
    # Obter leads para cada estágio do funil
    leads_novos = Lead.objects.filter(status='novo').order_by('-data_criacao')
    leads_contatados = Lead.objects.filter(status='contatado').order_by('-data_ultimo_contato')
    leads_qualificados = Lead.objects.filter(status='qualificado').order_by('-data_ultimo_contato')
    leads_negociacao = Lead.objects.filter(status='negociacao').order_by('-data_ultimo_contato')
    leads_fechados = Lead.objects.filter(status='fechado').order_by('-data_modificacao')
    leads_perdidos = Lead.objects.filter(status='perdido').order_by('-data_modificacao')
    
    # Estatísticas do funil
    total_leads = Lead.objects.count()
    taxa_conversao = 0
    
    if total_leads > 0:
        taxa_conversao = (leads_fechados.count() / total_leads) * 100
      # Resumo financeiro se disponível
    valor_interesse_total = sum(lead.valor_interesse or 0 for lead in Lead.objects.filter(status__in=['contatado', 'qualificado', 'negociacao']))
    valor_fechado = sum(lead.valor_interesse or 0 for lead in leads_fechados)
    
    context = {
        'leads_novos': leads_novos,
        'leads_contatados': leads_contatados,
        'leads_qualificados': leads_qualificados,
        'leads_negociacao': leads_negociacao,
        'leads_fechados': leads_fechados,
        'leads_perdidos': leads_perdidos,
        'total_leads': total_leads,
        'taxa_conversao': taxa_conversao,
        'valor_potencial': valor_interesse_total,
        'valor_fechado': valor_fechado,
    }
    
    return render(request, 'vendedores/utils/funil_vendas.html', context)

@login_required
def api_leads_disponiveis(request):
    """API para retornar os leads disponíveis para o vendedor em formato JSON com paginação."""
    vendedor = request.user
    
    # Busca leads que não foram contatadas nos últimos 3 dias pelo usuário atual
    todas_leads = Lead.objects.filter(status__in=['novo', 'contatado', 'qualificado'])
    
    # Aplicar filtros da URL
    status_filter = request.GET.get('status_filter')
    interesse_filter = request.GET.get('interesse_filter')
    prioridade_filter = request.GET.get('prioridade_filter')
    search_term = request.GET.get('search', '').strip()
    
    if status_filter:
        todas_leads = todas_leads.filter(status=status_filter)
    if interesse_filter:
        todas_leads = todas_leads.filter(interesse=interesse_filter)
    if prioridade_filter:
        todas_leads = todas_leads.filter(prioridade=prioridade_filter)
    
    # Aplicar filtro de busca
    if search_term:
        from django.db.models import Q
        search_filter = Q(nome__icontains=search_term) | Q(email__icontains=search_term) | Q(telefone__icontains=search_term) | Q(whatsapp__icontains=search_term)
        todas_leads = todas_leads.filter(search_filter)
    
    # Verificar quais leads estão disponíveis para contato
    leads_disponiveis = []
    for lead in todas_leads:
        if TentativaContato.pode_contatar(lead, vendedor):
            # Verifica se a lead foi contatada recentemente por outro vendedor
            lead.contatada_recentemente = TentativaContato.foi_contatado_recentemente(lead)
            # Se a lead foi contatada por alguém e o usuário não é um admin ou supervisor,
            # verifica se o vendedor atual já contatou esta lead antes
            if lead.contatada_recentemente and not request.user.profile.has_role_or_higher('supervisor'):
                # Apenas mostra a lead se o próprio vendedor já tentou contato com ela antes
                if TentativaContato.objects.filter(lead=lead, vendedor=vendedor).exists():
                    leads_disponiveis.append(lead)
            else:
                # Lead não foi contatada recentemente ou usuário é admin
                leads_disponiveis.append(lead)
    
    # Implementar paginação
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    # Calcular índices de início e fim para a página solicitada
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # Total de itens e total de páginas
    total_items = len(leads_disponiveis)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
    
    # Paginar os leads disponíveis
    paginated_leads = leads_disponiveis[start_index:end_index]
    
    # Converter leads para formato JSON
    leads_data = []
    for lead in paginated_leads:
        # Obter a última tentativa de contato
        ultima_tentativa = TentativaContato.objects.filter(lead=lead).order_by('-data_hora').first()
        ultimo_contato = ultima_tentativa.data_hora if ultima_tentativa else None
        
        lead_dict = {
            'id': lead.id,
            'nome': lead.nome,
            'email': lead.email,
            'telefone': lead.telefone,
            'whatsapp': lead.whatsapp,
            'status': lead.status,
            'interesse': lead.interesse,
            'ultimo_contato': ultimo_contato.isoformat() if ultimo_contato else None,
            'contatada_recentemente': lead.contatada_recentemente,
        }
        leads_data.append(lead_dict)
    
    # Retornar resposta JSON com os dados dos leads e informações de paginação
    response_data = {
        'leads': leads_data,
        'pagination': {
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': page < total_pages,
            'has_previous': page > 1,
        }
    }
    
    return JsonResponse(response_data, safe=False)