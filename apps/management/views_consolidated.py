"""
Views for the management application.
Includes administrative panels, user management, and performance reporting.
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
import json

from leads.models import Lead
from vendedores.models import TentativaContato
from .models import Profile
from .forms_consolidated import FuncionarioForm, FuncionarioEditForm, PasswordChangeForm
from .utils import export_to_csv, calculate_percentage
from .decorators import admin_required, supervisor_or_admin_required, supervisor_required


@supervisor_or_admin_required
def painel_admin(request):
    """
    Administrative dashboard with key performance metrics.
    Accessible to supervisors and admins.
    """
    # Main metrics
    total_funcionarios = User.objects.filter(
        profile__role__in=['vendedor', 'supervisor'], 
        is_active=True
    ).count()
    total_leads = Lead.objects.count()
    total_contatos = TentativaContato.objects.count()
    
    # Contacts per salesperson for main chart
    contatos_por_funcionario = []
    
    # Filter only sales reps (excluding supervisors and admins)
    vendedores = User.objects.filter(is_active=True, profile__role='vendedor')
    
    for vendedor in vendedores:
        total_contatos_vendedor = TentativaContato.objects.filter(vendedor=vendedor).count()
        contatos_sucesso_vendedor = TentativaContato.objects.filter(vendedor=vendedor, resultado='sucesso').count()
        taxa_sucesso_vendedor = calculate_percentage(contatos_sucesso_vendedor, total_contatos_vendedor)
        leads_convertidos_vendedor = Lead.objects.filter(responsavel=vendedor, status='fechado').count()
        
        contatos_por_funcionario.append({
            'vendedor_id': vendedor.id,
            'vendedor__username': vendedor.username,
            'vendedor__first_name': vendedor.first_name,
            'vendedor__last_name': vendedor.last_name,
            'total': total_contatos_vendedor,
            'taxa_sucesso': round(taxa_sucesso_vendedor, 1),
            'leads_convertidos': leads_convertidos_vendedor
        })
    
    # Sort by total contacts
    contatos_por_funcionario.sort(key=lambda x: x['total'], reverse=True)
    
    # Productivity calculation - average contacts per employee
    produtividade_media = calculate_percentage(total_contatos, total_funcionarios, 0)
    
    # Successful contacts
    contatos_sucesso = TentativaContato.objects.filter(resultado='sucesso').count()
    taxa_sucesso = calculate_percentage(contatos_sucesso, total_contatos)
    
    # Lead metrics
    leads_novos = Lead.objects.filter(status='novo').count()
    leads_qualificados = Lead.objects.filter(status='qualificado').count()
    leads_propostas = Lead.objects.filter(status='proposta').count()
    leads_fechados = Lead.objects.filter(status='fechado').count()
    
    # Data for lead status chart
    status_leads = [
        {'status': 'Novo', 'quantidade': leads_novos},
        {'status': 'Qualificado', 'quantidade': leads_qualificados},
        {'status': 'Proposta', 'quantidade': leads_propostas},
        {'status': 'Fechado', 'quantidade': leads_fechados},
        {
            'status': 'Outros', 
            'quantidade': total_leads - leads_novos - leads_qualificados - leads_propostas - leads_fechados
        },
    ]
    
    # Recent contacts for analysis
    hoje = timezone.now().date()
    contatos_hoje = TentativaContato.objects.filter(data_hora__date=hoje).count()
    contatos_semana = TentativaContato.objects.filter(
        data_hora__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Data for contacts in last 7 days chart
    contatos_ultimos_dias = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        contatos = TentativaContato.objects.filter(data_hora__date=dia).count()
        contatos_ultimos_dias.append({
            'dia': dia.strftime('%d/%m'),
            'contatos': contatos
        })
    
    # Additional metrics - Lead Conversion
    leads_convertidos = Lead.objects.filter(status='fechado').count()
    taxa_conversao = calculate_percentage(leads_convertidos, total_leads)
    
    # Performance metrics by lead source
    leads_por_origem = list(Lead.objects
        .values('fonte')
        .annotate(total=models.Count('id'))
        .order_by('-total'))
    
    # Leads by month (last 6 months)
    leads_por_mes = []
    for i in range(5, -1, -1):
        mes_atual = hoje.replace(day=1) - timedelta(days=i*30)
        mes_seguinte = mes_atual.replace(day=28) + timedelta(days=4)
        mes_seguinte = mes_seguinte.replace(day=1)

        total = Lead.objects.filter(
            data_criacao__gte=mes_atual,
            data_criacao__lt=mes_seguinte
        ).count()
        leads_por_mes.append({
            'mes': mes_atual.strftime('%m/%Y'),
            'total': total
        })
    
    return render(request, 'management/painel_admin.html', {
        'total_funcionarios': total_funcionarios,
        'total_leads': total_leads,
        'total_contatos': total_contatos,
        'contatos_por_funcionario': contatos_por_funcionario,  # Raw data for template
        'contatos_por_funcionario_json': json.dumps(contatos_por_funcionario),  # JSON data for JavaScript
        'contatos_hoje': contatos_hoje,
        'contatos_semana': contatos_semana,
        'produtividade_media': round(produtividade_media, 1),
        'contatos_sucesso': contatos_sucesso,
        'taxa_sucesso': round(taxa_sucesso, 1),
        'status_leads': json.dumps(status_leads),
        'contatos_ultimos_dias': json.dumps(contatos_ultimos_dias),
        'taxa_conversao': round(taxa_conversao, 1),
        'leads_por_origem': json.dumps(leads_por_origem),
        'leads_por_mes': json.dumps(leads_por_mes),
    })


@supervisor_or_admin_required
def vendedores_list(request):
    """List all sales representatives (excluding supervisors and admins)."""
    vendedores = User.objects.filter(profile__role='vendedor').select_related('profile')
    return render(request, 'management/vendedores.html', {'funcionarios': vendedores})


@admin_required
def funcionarios_list(request):
    """
    List all employees (sales reps and supervisors).
    Accessible only to administrators.
    """
    funcionarios = User.objects.filter(
        profile__role__in=['vendedor', 'supervisor']
    ).select_related('profile')
    return render(request, 'management/funcionarios.html', {'funcionarios': funcionarios})


@admin_required
def cadastrar_funcionario(request):
    """Create a new employee (user + profile)."""
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'Funcionário cadastrado com sucesso como {user.profile.get_role_display()}!'
            )
            return redirect('management:funcionarios')
    else:
        form = FuncionarioForm()
    return render(request, 'management/cadastrar_funcionario.html', {'form': form})


@admin_required
def editar_funcionario(request, user_id):
    """Edit an existing employee."""
    funcionario = get_object_or_404(
        User, 
        id=user_id,
        profile__role__in=['vendedor', 'supervisor']
    )
    
    if request.method == 'POST':
        form = FuncionarioEditForm(request.POST, instance=funcionario)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'Informações do funcionário {user.get_full_name() or user.username} atualizadas com sucesso!'
            )
            return redirect('management:detalhes_funcionario', user_id=user_id)
    else:
        form = FuncionarioEditForm(instance=funcionario)
    
    return render(request, 'management/editar_funcionario.html', {
        'form': form,
        'funcionario': funcionario
    })


@admin_required
def excluir_funcionario(request, user_id):
    """Delete an employee (user + profile)."""
    funcionario = get_object_or_404(
        User, 
        id=user_id,
        profile__role__in=['vendedor', 'supervisor']
    )
    
    if request.method == 'POST':
        nome = funcionario.get_full_name() or funcionario.username
        funcionario.delete()
        messages.success(request, f'Funcionário {nome} excluído com sucesso!')
        return redirect('management:funcionarios')
    
    return render(request, 'management/confirmar_exclusao_funcionario.html', {
        'funcionario': funcionario
    })


@supervisor_or_admin_required
def detalhes_funcionario(request, user_id):
    """
    Show detailed metrics and performance data for a specific employee.
    """
    funcionario = get_object_or_404(
        User, 
        id=user_id,
        profile__role__in=['vendedor', 'supervisor']
    )
    
    # All contacts by the employee
    contatos = TentativaContato.objects.filter(vendedor=funcionario)
    total_contatos = contatos.count()
    
    # Successful contacts
    contatos_sucesso = contatos.filter(resultado='sucesso').count()
    taxa_sucesso = calculate_percentage(contatos_sucesso, total_contatos)
    
    # Current assigned leads
    leads_designados = Lead.objects.filter(responsavel=funcionario).count()
    
    # Contacts in the last 30 days for chart
    hoje = timezone.now().date()
    contatos_por_dia = []
    
    for i in range(29, -1, -1):
        dia = hoje - timedelta(days=i)
        contatos_dia = contatos.filter(data_hora__date=dia).count()
        contatos_por_dia.append({
            'dia': dia.strftime('%d/%m'),
            'contatos': contatos_dia
        })
    
    # Contact result distribution
    resultados_contatos = [
        {
            'resultado': 'Sucesso',
            'total': contatos.filter(resultado='sucesso').count(),
        },
        {
            'resultado': 'Não Atendeu',
            'total': contatos.filter(resultado='nao_atendeu').count(),
        },
        {
            'resultado': 'Ocupado',
            'total': contatos.filter(resultado='ocupado').count(),
        },
        {
            'resultado': 'Número Inválido',
            'total': contatos.filter(resultado='numero_invalido').count(),
        },
        {
            'resultado': 'Outro',
            'total': contatos.filter(resultado='outro').count(),
        },
    ]
    
    # Contacts by day of week
    contatos_por_dia_semana = [0, 0, 0, 0, 0, 0, 0]  # Mon-Sun
    for contato in contatos:
        dia_semana = contato.data_hora.weekday()
        contatos_por_dia_semana[dia_semana] += 1
    
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    dados_dias_semana = [
        {'dia': dia, 'contatos': total} for dia, total in zip(dias_semana, contatos_por_dia_semana)
    ]
    
    # Advanced metrics - Comparison with team average
    total_vendedores = User.objects.filter(profile__role='vendedor').count()
    media_contatos_por_vendedor = (TentativaContato.objects.count() / total_vendedores
                                  if total_vendedores > 0 else 0)
    desempenho_relativo = calculate_percentage(total_contatos, media_contatos_por_vendedor)
    
    # Converted leads by employee
    leads_convertidos = Lead.objects.filter(responsavel=funcionario, status='fechado').count()
    taxa_conversao_funcionario = calculate_percentage(leads_convertidos, leads_designados)
    
    # Additional metrics for new charts
    # 1. Productivity trend (last 5 months)
    produtividade_mensal = []
    for i in range(4, -1, -1):
        mes_atual = hoje.replace(day=1) - timedelta(days=i*30)
        mes_seguinte = mes_atual.replace(day=28) + timedelta(days=4)
        mes_seguinte = mes_seguinte.replace(day=1)

        total_contatos_mes = contatos.filter(
            data_hora__gte=mes_atual,
            data_hora__lt=mes_seguinte
        ).count()
        
        produtividade_mensal.append({
            'mes': mes_atual.strftime('%b/%Y'),
            'contatos': total_contatos_mes
        })
    
    # 2. Contact result comparison by type
    resultados_detalhados = []
    tipos_resultado = ['sucesso', 'nao_atendeu', 'ocupado', 'numero_invalido', 'outro']
    nomes_resultado = ['Sucesso', 'Não Atendeu', 'Ocupado', 'Número Inválido', 'Outro']
    
    for tipo, nome in zip(tipos_resultado, nomes_resultado):
        # Employee total
        contatos_tipo = contatos.filter(resultado=tipo).count()
        # Team average
        media_equipe = (TentativaContato.objects.filter(resultado=tipo).count() / total_vendedores
                       if total_vendedores > 0 else 0)
        
        resultados_detalhados.append({
            'tipo': nome,
            'funcionario': contatos_tipo,
            'media_equipe': round(media_equipe, 1)
        })
    
    # 3. Conversion efficiency (success rate by day of week)
    eficiencia_dias = []
    for dia in range(7):
        contatos_dia = contatos.filter(data_hora__week_day=dia+1)  # Django uses 1-7 for Sun-Sat
        total_dia = contatos_dia.count()
        sucesso_dia = contatos_dia.filter(resultado='sucesso').count()
        eficiencia_dias.append({
            'dia': dias_semana[dia],
            'taxa': calculate_percentage(sucesso_dia, total_dia)
        })
    
    return render(request, 'management/detalhes_funcionario.html', {
        'funcionario': funcionario,
        'total_contatos': total_contatos,
        'contatos_sucesso': contatos_sucesso,
        'taxa_sucesso': round(taxa_sucesso, 1),
        'leads_designados': leads_designados,
        'contatos_por_dia': json.dumps(contatos_por_dia),
        'resultados_contatos': json.dumps(resultados_contatos),
        'dados_dias_semana': json.dumps(dados_dias_semana),
        'contatos_recentes': contatos.order_by('-data_hora')[:10],
        'desempenho_relativo': round(desempenho_relativo, 1),
        'leads_convertidos': leads_convertidos,
        'taxa_conversao_funcionario': round(taxa_conversao_funcionario, 1),
        # New data for detailed charts
        'produtividade_mensal': json.dumps(produtividade_mensal),
        'resultados_detalhados': json.dumps(resultados_detalhados),
        'eficiencia_dias': json.dumps(eficiencia_dias),
        'media_equipe_taxa_sucesso': round(
            calculate_percentage(TentativaContato.objects.filter(resultado='sucesso').count(),
                                TentativaContato.objects.count()), 1
        )
    })


@login_required
def alterar_senha(request):
    """Allow user to change their password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data['current_password']):
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('management:perfil')
            else:
                messages.error(request, 'Senha atual incorreta.')
    else:
        form = PasswordChangeForm()
    
    return render(request, 'management/alterar_senha.html', {'form': form})


@login_required
def perfil_usuario(request):
    """Show and edit user's own profile."""
    user = request.user
    
    if request.method == 'POST':
        # Only allow editing personal info, not role
        if user.first_name != request.POST.get('first_name') or \
           user.last_name != request.POST.get('last_name') or \
           user.email != request.POST.get('email') or \
           user.profile.phone != request.POST.get('phone') or \
           user.profile.bio != request.POST.get('bio'):
            
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            user.profile.phone = request.POST.get('phone', '')
            user.profile.bio = request.POST.get('bio', '')
            user.profile.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
        
        return redirect('management:perfil')
    
    return render(request, 'management/perfil.html', {'user': user})


@admin_required
def exportar_funcionarios(request):
    """Export employee list to CSV."""
    funcionarios = User.objects.filter(profile__role__in=['vendedor', 'supervisor'])
    dados = []
    
    for funcionario in funcionarios:
        contatos = TentativaContato.objects.filter(vendedor=funcionario).count()
        contatos_sucesso = TentativaContato.objects.filter(vendedor=funcionario, resultado='sucesso').count()
        leads_designados = Lead.objects.filter(responsavel=funcionario).count()
        leads_convertidos = Lead.objects.filter(responsavel=funcionario, status='fechado').count()
        
        dados.append({
            'username': funcionario.username,
            'nome': funcionario.get_full_name() or funcionario.username,
            'email': funcionario.email,
            'role': funcionario.profile.get_role_display(),
            'ativo': 'Sim' if funcionario.is_active else 'Não',
            'total_contatos': contatos,
            'contatos_sucesso': contatos_sucesso,
            'taxa_sucesso': f"{round(calculate_percentage(contatos_sucesso, contatos), 1)}%",
            'leads_designados': leads_designados,
            'leads_convertidos': leads_convertidos,
            'taxa_conversao': f"{round(calculate_percentage(leads_convertidos, leads_designados), 1)}%",
            'data_criacao': funcionario.date_joined.strftime('%d/%m/%Y')
        })
    
    headers = {
        'username': 'Usuário',
        'nome': 'Nome Completo',
        'email': 'Email',
        'role': 'Função',
        'ativo': 'Ativo',
        'total_contatos': 'Total de Contatos',
        'contatos_sucesso': 'Contatos com Sucesso',
        'taxa_sucesso': 'Taxa de Sucesso',
        'leads_designados': 'Leads Designados',
        'leads_convertidos': 'Leads Convertidos',
        'taxa_conversao': 'Taxa de Conversão',
        'data_criacao': 'Data de Cadastro'
    }
    
    return export_to_csv(dados, 'funcionarios', headers)


@admin_required
def exportar_contatos(request, user_id=None):
    """Export contact list to CSV (overall or by employee)."""
    if user_id:
        funcionario = get_object_or_404(
            User, 
            id=user_id,
            profile__role__in=['vendedor', 'supervisor']
        )
        contatos = TentativaContato.objects.filter(vendedor=funcionario)
        filename = f'contatos_{funcionario.username}'
    else:
        contatos = TentativaContato.objects.all()
        filename = 'todos_contatos'
    
    dados = []
    for contato in contatos:
        dados.append({
            'data_hora': contato.data_hora.strftime('%d/%m/%Y %H:%M'),
            'lead': contato.lead.nome if contato.lead else 'Não especificado',
            'vendedor': contato.vendedor.get_full_name() or contato.vendedor.username,
            'resultado': dict(TentativaContato._meta.get_field('resultado').choices).get(contato.resultado, contato.resultado),
            'observacoes': contato.observacoes or ''
        })
    
    headers = {
        'data_hora': 'Data/Hora',
        'lead': 'Lead',
        'vendedor': 'Vendedor',
        'resultado': 'Resultado',
        'observacoes': 'Observações'
    }
    
    return export_to_csv(dados, filename, headers)


@admin_required
def exportar_leads(request):
    """Export leads list to CSV."""
    leads = Lead.objects.all()
    dados = []
    
    for lead in leads:
        dados.append({
            'nome': lead.nome,
            'email': lead.email or '',
            'telefone': lead.telefone or '',
            'status': dict(Lead._meta.get_field('status').choices).get(lead.status, lead.status),
            'origem': dict(Lead._meta.get_field('fonte').choices).get(lead.fonte, lead.fonte),
            'interesse': dict(Lead._meta.get_field('interesse').choices).get(lead.interesse, lead.interesse),
            'responsavel': lead.responsavel.get_full_name() if lead.responsavel else 'Não atribuído',
            'data_criacao': lead.data_criacao.strftime('%d/%m/%Y') if hasattr(lead, 'data_criacao') else '',
            'valor_interesse': f"R$ {lead.valor_interesse}" if hasattr(lead, 'valor_interesse') and lead.valor_interesse else 'Não definido'
        })
    
    headers = {
        'nome': 'Nome',
        'email': 'Email',
        'telefone': 'Telefone',
        'status': 'Status',
        'origem': 'Origem',
        'interesse': 'Interesse',
        'responsavel': 'Responsável',
        'data_criacao': 'Data de Criação',
        'valor_interesse': 'Valor de Interesse'
    }
    
    return export_to_csv(dados, 'leads', headers)


@supervisor_or_admin_required
def relatorio_desempenho(request):
    """
    Performance report for the team, accessible to supervisors and admins.
    Shows general metrics without access to administrative functions.
    """
    # Filter only sales reps (excluding supervisors and admins)
    vendedores = User.objects.filter(is_active=True, profile__role='vendedor')
    total_vendedores = vendedores.count()
    
    # General metrics
    total_contatos = TentativaContato.objects.count()
    contatos_sucesso = TentativaContato.objects.filter(resultado='sucesso').count()
    taxa_sucesso_geral = calculate_percentage(contatos_sucesso, total_contatos)
    
    # Performance data by sales rep
    desempenho_vendedores = []
    
    for vendedor in vendedores:
        contatos_vendedor = TentativaContato.objects.filter(vendedor=vendedor)
        total_contatos_vendedor = contatos_vendedor.count()
        
        # Performance calculations
        contatos_sucesso_vendedor = contatos_vendedor.filter(resultado='sucesso').count()
        taxa_sucesso_vendedor = calculate_percentage(contatos_sucesso_vendedor, total_contatos_vendedor)
        
        # Recent contacts (last 7 days)
        contatos_recentes = contatos_vendedor.filter(
            data_hora__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Daily average of contacts in the last week
        media_diaria = contatos_recentes / 7
        
        desempenho_vendedores.append({
            'id': vendedor.id,
            'nome': vendedor.get_full_name() or vendedor.username,
            'total_contatos': total_contatos_vendedor,
            'contatos_sucesso': contatos_sucesso_vendedor,
            'taxa_sucesso': round(taxa_sucesso_vendedor, 1),
            'contatos_recentes': contatos_recentes,
            'media_diaria': round(media_diaria, 1)
        })
    
    # Sort by number of contacts (most active first)
    desempenho_vendedores.sort(key=lambda x: x['total_contatos'], reverse=True)
    
    # Data for performance chart
    labels_vendedores = [v['nome'] for v in desempenho_vendedores[:10]]  # Top 10 sales reps
    dados_contatos = [v['total_contatos'] for v in desempenho_vendedores[:10]]
    dados_sucesso = [v['contatos_sucesso'] for v in desempenho_vendedores[:10]]
    
    # Historical data - Last 7 days
    historico_contatos = []
    hoje = timezone.now().date()
    
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        contatos_dia = TentativaContato.objects.filter(data_hora__date=dia).count()
        
        historico_contatos.append({
            'dia': dia.strftime('%d/%m'),
            'contatos': contatos_dia
        })
    
    return render(request, 'management/relatorio_desempenho.html', {
        'total_vendedores': total_vendedores,
        'total_contatos': total_contatos,
        'contatos_sucesso': contatos_sucesso,
        'taxa_sucesso_geral': round(taxa_sucesso_geral, 1),
        'desempenho_vendedores': desempenho_vendedores,
        'labels_vendedores': json.dumps(labels_vendedores),
        'dados_contatos': json.dumps(dados_contatos),
        'dados_sucesso': json.dumps(dados_sucesso),
        'historico_contatos': json.dumps(historico_contatos),
    })
