"""
Lions CRM - Módulo de análise de dados para o painel de gerência
Desenvolvido para facilitar a análise e visualização de dados do CRM
Utiliza pandas e numpy para manipulação de dados e cálculo de métricas
Versão corrigida: 20 de junho de 2025
"""

from django.db import models
from django.db.models import Count, F, Sum, Avg, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce, TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta, date
from leads.models import Lead
from vendedores.models import TentativaContato
from django.contrib.auth.models import User

class DashboardAnalytics:
    """Classe principal para geração de dados analíticos para o dashboard gerencial"""
    
    @staticmethod
    def get_all_metrics():
        """Retorna todas as métricas principais em um único dicionário"""
        metrics = {
            **DashboardAnalytics.get_general_metrics(),
            **DashboardAnalytics.get_daily_stats(),
            **DashboardAnalytics.get_leads_overview(),
            **DashboardAnalytics.get_contact_stats(),
            **DashboardAnalytics.get_conversion_stats(),
        }
        return metrics

    @staticmethod
    def get_general_metrics():
        """Retorna métricas gerais básicas como contagens e totais"""
        today = timezone.now().date()
        total_funcionarios = User.objects.filter(profile__role__in=['vendedor', 'supervisor'], is_active=True).count()
        total_leads = Lead.objects.count()
        total_contatos = TentativaContato.objects.count()
        leads_ativos = Lead.objects.exclude(status='fechado').exclude(status='perdido').count()
        
        # Calcular alterações percentuais comparando com 30 dias atrás
        thirty_days_ago = today - timedelta(days=30)
        
        leads_last_30days = Lead.objects.filter(data_criacao__gte=thirty_days_ago).count()
        leads_previous_30days = Lead.objects.filter(
            data_criacao__lt=thirty_days_ago,
            data_criacao__gte=thirty_days_ago - timedelta(days=30)
        ).count()
        
        leads_percent_change = (
            ((leads_last_30days - leads_previous_30days) / leads_previous_30days * 100)
            if leads_previous_30days > 0 else 0
        )
        
        # Contatos com sucesso
        contatos_sucesso = TentativaContato.objects.filter(resultado='sucesso').count()
        taxa_sucesso = (contatos_sucesso / total_contatos * 100) if total_contatos > 0 else 0
        
        # Leads convertidos
        leads_convertidos = Lead.objects.filter(status='fechado').count()
        taxa_conversao = (leads_convertidos / total_leads * 100) if total_leads > 0 else 0
        
        # Produtividade média
        produtividade_media = total_contatos / total_funcionarios if total_funcionarios > 0 else 0
        
        return {
            'total_funcionarios': total_funcionarios,
            'total_leads': total_leads,
            'total_contatos': total_contatos,
            'leads_ativos': leads_ativos,
            'leads_percent_change': round(leads_percent_change, 1),
            'contatos_sucesso': contatos_sucesso,
            'taxa_sucesso': round(taxa_sucesso, 1),
            'taxa_conversao': round(taxa_conversao, 1),
            'produtividade_media': round(produtividade_media, 1),
        }
    
    @staticmethod
    def get_daily_stats():
        """Retorna estatísticas diárias e semanais para análise de tendências"""
        today = timezone.now().date()
        
        # Contatos hoje e na última semana
        contatos_hoje = TentativaContato.objects.filter(data_hora__date=today).count()
        
        # Contatos por dia nos últimos 7 dias
        contatos_ultimos_dias = []
        for i in range(6, -1, -1):
            dia = today - timedelta(days=i)
            contatos = TentativaContato.objects.filter(data_hora__date=dia).count()
            contatos_ultimos_dias.append({
                'dia': dia.strftime('%d/%m'),
                'contatos': contatos
            })
        
        # Contatos por semana (últimas 4 semanas)
        semanas = []
        for i in range(3, -1, -1):
            inicio_semana = today - timedelta(days=today.weekday() + 7*i)
            fim_semana = inicio_semana + timedelta(days=6)
            contatos_semana = TentativaContato.objects.filter(
                data_hora__date__gte=inicio_semana,
                data_hora__date__lte=fim_semana
            ).count()
            
            semanas.append({
                'semana': f'{inicio_semana.strftime("%d/%m")} - {fim_semana.strftime("%d/%m")}',
                'contatos': contatos_semana
            })
        
        # Análise de horas mais produtivas
        horas_produtivas = (TentativaContato.objects
            .annotate(hora=models.functions.ExtractHour('data_hora'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora'))
        
        # Converter para lista para uso em gráficos
        horas_produtivas_list = [
            {'hora': f'{item["hora"]:02d}:00', 'total': item['total']}
            for item in horas_produtivas
        ]
        
        return {
            'contatos_hoje': contatos_hoje,
            'contatos_ultimos_dias': contatos_ultimos_dias,
            'contatos_por_semana': semanas,
            'horas_produtivas': horas_produtivas_list,
        }
    
    @staticmethod
    def get_leads_overview():
        """Retorna visão geral dos leads por status, origem e período"""
        # Status dos leads
        leads_por_status = []
        status_counts = Lead.objects.values('status').annotate(quantidade=Count('id'))
        
        # Mapear status para nomes amigáveis
        status_mapping = {
            'novo': 'Novo',
            'qualificado': 'Qualificado',
            'proposta': 'Proposta',
            'fechado': 'Fechado',
            'perdido': 'Perdido'
        }
        
        for status in status_counts:
            status_nome = status_mapping.get(status['status'], status['status'].capitalize())
            leads_por_status.append({
                'status': status_nome,
                'quantidade': status['quantidade']
            })
        
        # Leads por origem
        leads_por_origem = list(
            Lead.objects.values('fonte')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        
        # Leads por mês (últimos 6 meses)
        today = timezone.now().date()
        leads_por_mes = []
        
        for i in range(5, -1, -1):
            mes_atual = date(today.year, today.month, 1) - timedelta(days=i*30)
            mes_seguinte = (mes_atual + timedelta(days=32)).replace(day=1)
            
            total = Lead.objects.filter(
                data_criacao__gte=mes_atual,
                data_criacao__lt=mes_seguinte
            ).count()
            
            leads_por_mes.append({
                'mes': mes_atual.strftime('%m/%Y'),
                'total': total
            })
          # Construir manualmente a distribuição por dia da semana para compatibilidade com SQLite
        leads_por_dia_semana_list = []
        dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
          # Para cada lead, determinar o dia da semana
        for lead in Lead.objects.all():
            if hasattr(lead, 'data_criacao') and lead.data_criacao:
                # Obter o dia da semana (0 = segunda, 6 = domingo)
                # Converter para formato onde 0 = domingo para compatibilidade
                dia_index = lead.data_criacao.weekday()
                dia_index = (dia_index + 1) % 7  # Converter para domingo=0, segunda=1, etc.
                
                # Verificar se o dia já existe na lista
                dia_encontrado = False
                for item in leads_por_dia_semana_list:
                    if item['dia'] == dias_semana[dia_index]:
                        item['total'] += 1
                        dia_encontrado = True
                        break
                
                # Se não encontrou, adicionar novo dia
                if not dia_encontrado:
                    leads_por_dia_semana_list.append({
                        'dia': dias_semana[dia_index],
                        'total': 1
                    })
        
        # Garantir que todos os dias da semana estejam representados
        for i, dia in enumerate(dias_semana):
            if not any(item['dia'] == dia for item in leads_por_dia_semana_list):
                leads_por_dia_semana_list.append({
                    'dia': dia,
                    'total': 0
                })
        
        return {
            'leads_por_status': leads_por_status,
            'leads_por_origem': leads_por_origem,
            'leads_por_mes': leads_por_mes,
            'leads_por_dia_semana': leads_por_dia_semana_list
        }
    
    @staticmethod
    def get_contact_stats():
        """Retorna estatísticas de contatos e tentativas"""
        # Resultados das tentativas de contato
        resultados_contatos = (TentativaContato.objects
            .values('resultado')
            .annotate(total=Count('id'))
            .order_by('-total'))
          # Média de tentativas por lead até sucesso
        # Modificado para considerar a estrutura correta do modelo
        total_tentativas = 0
        contagem_leads_com_sucesso = 0
        
        # Precisamos verificar o relacionamento correto entre Lead e TentativaContato
        # Vamos buscar as tentativas de contato com sucesso
        tentativas_sucesso = TentativaContato.objects.filter(resultado='sucesso').select_related('lead')
        
        # Conjunto de IDs de leads que tiveram tentativas bem-sucedidas
        lead_ids_sucesso = set()
        
        for tentativa in tentativas_sucesso:
            if hasattr(tentativa, 'lead') and tentativa.lead and tentativa.lead.id not in lead_ids_sucesso:
                lead_ids_sucesso.add(tentativa.lead.id)
                # Para cada lead, conta quantas tentativas foram feitas até o sucesso
                tentativas_lead = TentativaContato.objects.filter(
                    lead=tentativa.lead,
                    data_hora__lte=tentativa.data_hora
                ).count()
                
                total_tentativas += tentativas_lead
                contagem_leads_com_sucesso += 1        
        media_tentativas_sucesso = (
            total_tentativas / contagem_leads_com_sucesso
            if contagem_leads_com_sucesso > 0 else 0
        )
        
        # Taxa de resposta por resultado
        canais_contato = (TentativaContato.objects
            .values('resultado')
            .annotate(
                total=Count('id'),
                sucessos=Sum(Case(
                    When(resultado='sucesso', then=1),
                    default=0,
                    output_field=IntegerField()
                ))
            )
            .order_by('-total'))
        
        # Adicionar taxa de sucesso a cada canal
        for canal in canais_contato:
            canal['taxa_sucesso'] = (
                round(canal['sucessos'] / canal['total'] * 100, 1)
                if canal['total'] > 0 else 0
            )
        
        return {
            'resultados_contatos': list(resultados_contatos),
            'media_tentativas_sucesso': round(media_tentativas_sucesso, 1),
            'canais_contato': list(canais_contato)
        }
    
    @staticmethod
    def get_conversion_stats():
        """Calcula métricas de conversão e eficiência de vendas"""        # Tempo médio de conversão (dias entre criação do lead e última modificação para leads fechados)
        leads_fechados = Lead.objects.filter(status='fechado', data_modificacao__isnull=False)
        
        total_dias = 0
        for lead in leads_fechados:
            if lead.data_criacao and lead.data_modificacao:
                dias = (lead.data_modificacao.date() - lead.data_criacao.date()).days
                total_dias += dias
        
        tempo_medio_conversao = total_dias / leads_fechados.count() if leads_fechados.count() > 0 else 0
        
        # Taxa de conversão por origem
        conversao_por_origem = []
        origens = Lead.objects.values_list('fonte', flat=True).distinct()
        
        for origem in origens:
            total_origem = Lead.objects.filter(fonte=origem).count()
            convertidos_origem = Lead.objects.filter(fonte=origem, status='fechado').count()
            
            taxa = (convertidos_origem / total_origem * 100) if total_origem > 0 else 0
            
            conversao_por_origem.append({
                'origem': origem,
                'total': total_origem,
                'convertidos': convertidos_origem,
                'taxa': round(taxa, 1)
            })
        
        # Ordenar por taxa de conversão decrescente
        conversao_por_origem.sort(key=lambda x: x['taxa'], reverse=True)
        
        # Valor médio por lead convertido
        leads_com_valor = Lead.objects.filter(
            status='fechado',
            valor_interesse__isnull=False,
            valor_interesse__gt=0
        )
        
        valor_medio = 0
        if leads_com_valor.count() > 0:
            valor_medio = leads_com_valor.aggregate(avg=Avg('valor_interesse'))['avg'] or 0
        
        return {
            'tempo_medio_conversao': round(tempo_medio_conversao, 1),
            'conversao_por_origem': conversao_por_origem,
            'valor_medio_lead': round(valor_medio, 2)
        }
    
    @staticmethod
    def get_sales_team_performance():
        """Análise de desempenho da equipe de vendas"""
        vendedores = User.objects.filter(profile__role='vendedor', is_active=True)
        desempenho_vendedores = []
        
        today = timezone.now().date()
        inicio_mes = date(today.year, today.month, 1)
        
        for vendedor in vendedores:
            # Contatos realizados no mês atual
            contatos_mes = TentativaContato.objects.filter(
                vendedor=vendedor,
                data_hora__date__gte=inicio_mes
            ).count()
            
            # Leads ativos atualmente designados
            leads_ativos = Lead.objects.filter(
                responsavel=vendedor
            ).exclude(
                status__in=['fechado', 'perdido']
            ).count()
              # Leads convertidos no mês atual
            leads_convertidos_mes = Lead.objects.filter(
                responsavel=vendedor,
                status='fechado',
                data_modificacao__date__gte=inicio_mes  # Usamos data_modificacao em vez de data_fechamento
            ).count()
            
            # Contatos com sucesso no mês atual
            contatos_sucesso_mes = TentativaContato.objects.filter(
                vendedor=vendedor,
                resultado='sucesso',
                data_hora__date__gte=inicio_mes
            ).count()
            
            # Taxa de sucesso nos contatos
            taxa_sucesso = (
                contatos_sucesso_mes / contatos_mes * 100
                if contatos_mes > 0 else 0
            )
            
            # Adiciona os dados ao array
            desempenho_vendedores.append({
                'id': vendedor.id,
                'nome': f"{vendedor.first_name} {vendedor.last_name}",
                'contatos_mes': contatos_mes,
                'leads_ativos': leads_ativos,
                'leads_convertidos_mes': leads_convertidos_mes,
                'taxa_sucesso': round(taxa_sucesso, 1)
            })
        
        # Ordenar por leads convertidos no mês (decrescente)
        desempenho_vendedores.sort(key=lambda x: x['leads_convertidos_mes'], reverse=True)
        
        return desempenho_vendedores
    
    @staticmethod
    def format_for_charts(data_dict):
        """Converte os dicionários de dados para JSON para uso em gráficos"""
        formatted_data = {}
        
        for key, value in data_dict.items():
            if isinstance(value, list):
                formatted_data[key] = json.dumps(value)
            else:
                formatted_data[key] = value
        
        return formatted_data

def get_dashboard_data():
    """Função auxiliar para obter todos os dados formatados para o dashboard"""
    analytics = DashboardAnalytics()
    
    # Obter todas as métricas e estatísticas
    all_metrics = analytics.get_all_metrics()
    
    # Adicionar análise de desempenho da equipe
    all_metrics['desempenho_vendedores'] = analytics.get_sales_team_performance()
    
    # Formatar dados para gráficos
    return analytics.format_for_charts(all_metrics)
