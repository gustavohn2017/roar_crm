from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
import json
from leads.models import Lead
from vendedores.models import TentativaContato
from .forms import FuncionarioForm
from .utils import export_to_csv
from .decorators import admin_required, supervisor_or_admin_required

@supervisor_or_admin_required
def painel_admin(request):
    """
    Painel gerencial avançado com métricas em tempo real e gráficos interativos.
    Utiliza pandas para processamento de dados e análises estatísticas.
    """
    from .analytics import DashboardAnalytics, ReportGenerator
    
    # Inicializar analytics
    analytics = DashboardAnalytics()
    report_generator = ReportGenerator()
    
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    
    # === MÉTRICAS PRINCIPAIS USANDO ANALYTICS ===
    performance_metrics = analytics.get_performance_metrics()
    
    total_funcionarios = User.objects.filter(
        profile__role__in=['vendedor', 'supervisor'], 
        is_active=True
    ).count()
    total_contatos = TentativaContato.objects.count()
    
    # Receita potencial (estimativa)
    valor_medio_negocio = 50000  # Valor padrão, pode ser configurável
    receita_potencial = performance_metrics['leads_ativos'] * valor_medio_negocio
    receita_realizada = performance_metrics['leads_convertidos'] * valor_medio_negocio
    
    # === ANÁLISE DE PERFORMANCE POR VENDEDOR ===
    performance_vendedores = analytics.get_vendedor_performance()
    
    # === ANÁLISE DO FUNIL DE VENDAS ===
    funil_vendas = analytics.get_funil_vendas_analysis()
    
    # === ATIVIDADE EM TEMPO REAL ===
    atividade_tempo_real = analytics.get_real_time_activity()
    
    # === INSIGHTS PREDITIVOS ===
    insights_preditivos = analytics.get_predictive_insights()
    
    # === ANÁLISE TEMPORAL ===
    # Leads nos últimos 30 dias
    leads_30_dias = []
    for i in range(29, -1, -1):
        dia = hoje - timedelta(days=i)
        count = Lead.objects.filter(data_criacao__date=dia).count()
        leads_30_dias.append({
            'data': dia.strftime('%Y-%m-%d'),
            'data_label': dia.strftime('%d/%m'),
            'count': count
        })
    
    # === ANÁLISE POR ORIGEM ===
    leads_origem = Lead.objects.values('fonte').annotate(
        total=models.Count('id'),
        convertidos=models.Count('id', filter=models.Q(status='fechado')),
    ).order_by('-total')
    
    # Adicionar taxa de conversão
    for origem in leads_origem:
        origem['taxa_conversao'] = round(
            (origem['convertidos'] / origem['total'] * 100) if origem['total'] > 0 else 0, 2
        )
    
    # === MÉTRICAS DE TEMPO REAL ===
    contatos_hoje = TentativaContato.objects.filter(data_hora__date=hoje).count()
    
    # === PREVISÕES E TENDÊNCIAS ===
    # Análise de tendência dos últimos 7 dias
    leads_semana_anterior = Lead.objects.filter(
        data_criacao__gte=inicio_semana - timedelta(days=7),
        data_criacao__lt=inicio_semana
    ).count()
    leads_semana_atual = Lead.objects.filter(data_criacao__gte=inicio_semana).count()
    
    tendencia_leads = leads_semana_atual - leads_semana_anterior
    tendencia_percentual = round(
        (tendencia_leads / leads_semana_anterior * 100) if leads_semana_anterior > 0 else 0, 2
    )
    
    # === RELATÓRIO DE PERFORMANCE DO PERÍODO ===
    summary_30_dias = report_generator.generate_performance_summary(30)
    
    # === PREPARAÇÃO DOS DADOS PARA TEMPLATE ===
    context = {
        # Métricas principais
        'total_funcionarios': total_funcionarios,
        'total_leads': performance_metrics['total_leads'],
        'total_contatos': total_contatos,
        'leads_ativos': performance_metrics['leads_ativos'],
        'taxa_conversao': performance_metrics['taxa_conversao'],
        'receita_potencial': f"R$ {receita_potencial:,.2f}".replace(',', '.'),
        'receita_realizada': f"R$ {receita_realizada:,.2f}".replace(',', '.'),
        
        # Métricas tempo real
        'contatos_hoje': contatos_hoje,
        'leads_hoje': performance_metrics['leads_hoje'],
        'tendencia_leads': tendencia_leads,
        'tendencia_percentual': tendencia_percentual,
        
        # Insights preditivos
        'previsao_7_dias': sum(insights_preditivos['previsao_7_dias']),
        'tendencia_diaria': insights_preditivos['tendencia_diaria'],
        'media_30_dias': insights_preditivos['media_30_dias'],
        
        # Dados para gráficos (JSON)
        'performance_vendedores': performance_vendedores,
        'performance_vendedores_json': json.dumps(performance_vendedores),
        'leads_30_dias_json': json.dumps(leads_30_dias),
        'funil_vendas_json': json.dumps(funil_vendas),
        'leads_origem_json': json.dumps(list(leads_origem)),
        'contatos_por_hora_json': json.dumps(atividade_tempo_real),
        
        # Insights e relatórios
        'summary_periodo': summary_30_dias,
        'origem_stats': performance_metrics['origem_stats'],
        
        # Para compatibilidade com template existente
        'contatos_por_funcionario': performance_vendedores,
        'status_leads': json.dumps([
            {'status': item['status'], 'quantidade': item['count']} 
            for item in funil_vendas
        ]),
        'contatos_ultimos_dias': json.dumps([
            {'dia': item['data_label'], 'contatos': item['count']} 
            for item in leads_30_dias[-7:]
        ]),
        'leads_por_origem': json.dumps([
            {'fonte': item['fonte'], 'total': item['total']} 
            for item in leads_origem
        ]),
    }
    
    return render(request, 'gerencia/painel_admin.html', context)

@supervisor_or_admin_required
def vendedores(request):
    # Filtrar vendedores (excluindo supervisores e admins)
    vendedores = User.objects.filter(profile__role='vendedor')
    return render(request, 'gerencia/vendedores.html', {'funcionarios': vendedores})

@admin_required
def funcionarios(request):
    # Página para listar todos os funcionários (vendedores e supervisores)
    # Acessível apenas para administradores
    funcionarios = User.objects.filter(profile__role__in=['vendedor', 'supervisor'])
    return render(request, 'gerencia/funcionarios.html', {'funcionarios': funcionarios})

@admin_required
def cadastrar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Atualiza o perfil do usuário com o papel
            profile = user.profile
            profile.role = form.cleaned_data['role']
            profile.save()
            
            messages.success(request, f'Funcionário cadastrado com sucesso como {profile.get_role_display()}!')
            return redirect('gerencia:funcionarios')
    else:
        form = FuncionarioForm()
    return render(request, 'gerencia/cadastrar_funcionario.html', {'form': form})

@admin_required
def excluir_funcionario(request, user_id):
    funcionario = get_object_or_404(User, id=user_id, profile__role__in=['vendedor', 'supervisor'])
    funcionario.delete()
    messages.success(request, 'Funcionário excluído com sucesso!')
    return redirect('gerencia:funcionarios')

@supervisor_or_admin_required
def detalhes_funcionario(request, user_id):
    funcionario = get_object_or_404(User, id=user_id, profile__role__in=['vendedor', 'supervisor'])
    
    # Todos os contatos do funcionário
    contatos = TentativaContato.objects.filter(vendedor=funcionario)
    total_contatos = contatos.count()
    
    # Contatos com sucesso
    contatos_sucesso = contatos.filter(resultado='sucesso').count()
    taxa_sucesso = (contatos_sucesso / total_contatos * 100) if total_contatos > 0 else 0
    
    # Leads atuais designados
    leads_designados = Lead.objects.filter(responsavel=funcionario).count()
    
    # Contatos nos últimos 30 dias para o gráfico
    hoje = timezone.now().date()
    contatos_por_dia = []
    
    for i in range(29, -1, -1):
        dia = hoje - timedelta(days=i)
        contatos_dia = contatos.filter(data_hora__date=dia).count()
        contatos_por_dia.append({
            'dia': dia.strftime('%d/%m'),
            'contatos': contatos_dia
        })
    
    # Distribuição dos resultados dos contatos
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
      # Contatos por dia da semana
    contatos_por_dia_semana = [0, 0, 0, 0, 0, 0, 0]  # Seg a Dom
    for contato in contatos:
        dia_semana = contato.data_hora.weekday()
        # weekday() retorna 0=Segunda, 1=Terça, ..., 6=Domingo
        contatos_por_dia_semana[dia_semana] += 1
    
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    dados_dias_semana = [
        {'dia': dia, 'contatos': total} for dia, total in zip(dias_semana, contatos_por_dia_semana)
    ]
      # Métricas avançadas - Comparação com a média da equipe
    media_contatos_por_vendedor = TentativaContato.objects.count() / User.objects.filter(profile__role='vendedor').count() if User.objects.filter(profile__role='vendedor').count() > 0 else 0
    desempenho_relativo = (total_contatos / media_contatos_por_vendedor * 100) if media_contatos_por_vendedor > 0 else 0
    
    # Leads convertidos pelo funcionário
    leads_convertidos = Lead.objects.filter(responsavel=funcionario, status='fechado').count()
    taxa_conversao_funcionario = (leads_convertidos / leads_designados * 100) if leads_designados > 0 else 0
    
    # Métricas adicionais para os novos gráficos
    # 1. Tendência de produtividade (últimos 5 meses)
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
    
    # 2. Comparação de resultados por tipo de contato
    resultados_detalhados = []
    tipos_resultado = ['sucesso', 'nao_atendeu', 'ocupado', 'numero_invalido', 'outro']
    nomes_resultado = ['Sucesso', 'Não Atendeu', 'Ocupado', 'Número Inválido', 'Outro']
    
    for tipo, nome in zip(tipos_resultado, nomes_resultado):
        # Total do funcionário
        contatos_tipo = contatos.filter(resultado=tipo).count()
          # Média da equipe
        media_equipe = TentativaContato.objects.filter(resultado=tipo).count() / User.objects.filter(profile__role='vendedor').count() if User.objects.filter(profile__role='vendedor').count() > 0 else 0
        
        resultados_detalhados.append({
            'tipo': nome,
            'funcionario': contatos_tipo,
            'media_equipe': round(media_equipe, 1)
        })
      # 3. Eficiência de conversão (taxa de sucesso por dia da semana)
    eficiencia_dias = []
    for dia in range(7):
        contatos_dia = contatos.filter(data_hora__week_day=dia+1)  # Django usa 1-7 para domingo-sábado
        total_dia = contatos_dia.count()
        sucesso_dia = contatos_dia.filter(resultado='sucesso').count()
        eficiencia_dias.append({
            'dia': dias_semana[dia],
            'taxa': (sucesso_dia / total_dia * 100) if total_dia > 0 else 0
        })
    
    return render(request, 'gerencia/detalhes_funcionario.html', {
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
        # Novos dados para gráficos detalhados
        'produtividade_mensal': json.dumps(produtividade_mensal),
        'resultados_detalhados': json.dumps(resultados_detalhados),
        'eficiencia_dias': json.dumps(eficiencia_dias),
        'media_equipe_taxa_sucesso': round((TentativaContato.objects.filter(resultado='sucesso').count() / TentativaContato.objects.count() * 100) if TentativaContato.objects.count() > 0 else 0, 1)
    })

@admin_required
def exportar_funcionarios(request):
    """Exporta a lista de funcionários para CSV"""
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
            'ativo': 'Sim' if funcionario.is_active else 'Não',
            'total_contatos': contatos,
            'contatos_sucesso': contatos_sucesso,
            'taxa_sucesso': f"{round((contatos_sucesso / contatos * 100), 1)}%" if contatos > 0 else "0%",
            'leads_designados': leads_designados,
            'leads_convertidos': leads_convertidos,
            'taxa_conversao': f"{round((leads_convertidos / leads_designados * 100), 1)}%" if leads_designados > 0 else "0%",
            'data_criacao': funcionario.date_joined.strftime('%d/%m/%Y')
        })
    
    headers = {
        'username': 'Usuário',
        'nome': 'Nome Completo',
        'email': 'Email',
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
    """Exporta a lista de contatos para CSV (geral ou por funcionário)"""
    if user_id:
        funcionario = get_object_or_404(User, id=user_id, profile__role__in=['vendedor', 'supervisor'])
        contatos = TentativaContato.objects.filter(vendedor=funcionario)
        filename = f'contatos_{funcionario.username}'
    else:
        contatos = TentativaContato.objects.all()
        filename = 'todos_contatos'
    
    dados = []
    for contato in contatos:
        dados.append({
            'data_hora': contato.data_hora.strftime('%d/%m/%Y %H:%M'),
            'lead': contato.lead.nome,
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
    """Exporta a lista de leads para CSV"""
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
    Relatório de desempenho da equipe, acessível para supervisores e administradores.
    Mostra métricas gerais sem acesso a funcionalidades administrativas.
    """
    # Filtrar apenas os vendedores (excluindo supervisores e admins)
    vendedores = User.objects.filter(is_active=True, profile__role='vendedor')
    total_vendedores = vendedores.count()
    
    # Métricas gerais
    total_contatos = TentativaContato.objects.count()
    contatos_sucesso = TentativaContato.objects.filter(resultado='sucesso').count()
    taxa_sucesso_geral = (contatos_sucesso / total_contatos * 100) if total_contatos > 0 else 0
    
    # Dados de desempenho por vendedor
    desempenho_vendedores = []
    
    for vendedor in vendedores:
        contatos_vendedor = TentativaContato.objects.filter(vendedor=vendedor)
        total_contatos_vendedor = contatos_vendedor.count()
        
        # Cálculos de desempenho
        contatos_sucesso_vendedor = contatos_vendedor.filter(resultado='sucesso').count()
        taxa_sucesso_vendedor = (contatos_sucesso_vendedor / total_contatos_vendedor * 100) if total_contatos_vendedor > 0 else 0
        
        # Contatos recentes (últimos 7 dias)
        contatos_recentes = contatos_vendedor.filter(
            data_hora__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Média diária de contatos na última semana
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
    
    # Ordenar por número de contatos (mais ativos primeiro)
    desempenho_vendedores.sort(key=lambda x: x['total_contatos'], reverse=True)
    
    # Dados para gráfico de desempenho
    labels_vendedores = [v['nome'] for v in desempenho_vendedores[:10]]  # Top 10 vendedores
    dados_contatos = [v['total_contatos'] for v in desempenho_vendedores[:10]]
    dados_sucesso = [v['contatos_sucesso'] for v in desempenho_vendedores[:10]]
    
    # Dados históricos - Últimos 7 dias
    historico_contatos = []
    hoje = timezone.now().date()
    
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        contatos_dia = TentativaContato.objects.filter(data_hora__date=dia).count()
        
        historico_contatos.append({
            'dia': dia.strftime('%d/%m'),
            'contatos': contatos_dia
        })
    
    return render(request, 'gerencia/relatorio_desempenho.html', {
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

@login_required
def perfil_usuario(request):
    """
    Permite ao usuário visualizar e editar seu próprio perfil.
    """
    user = request.user
    
    # Se o formulário for enviado, processar os dados
    if request.method == 'POST':
        # Atualizar apenas os campos básicos do usuário
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        bio = request.POST.get('bio')
        
        # Atualizar o usuário
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        # Atualizar o perfil
        if hasattr(user, 'profile'):
            user.profile.phone = telefone
            user.profile.bio = bio
            user.profile.save()
            
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('gerencia:perfil')
    
    return render(request, 'gerencia/perfil_usuario.html', {
        'user': user
    })
