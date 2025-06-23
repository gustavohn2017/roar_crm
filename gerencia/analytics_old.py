"""
Módulo de analytics avançado para o painel gerencial.
Utiliza pandas e outras bibliotecas para análises estatísticas e geração de insights.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q, Avg, Sum
from django.contrib.auth.models import User
from leads.models import Lead
from vendedores.models import TentativaContato


class DashboardAnalytics:
    """Classe principal para análises do dashboard gerencial."""
    
    def __init__(self):
        self.hoje = timezone.now().date()
        self.inicio_mes = self.hoje.replace(day=1)
        self.inicio_semana = self.hoje - timedelta(days=self.hoje.weekday())
        
        # Converter para datetime timezone aware para comparações com pandas
        self.hoje_datetime = pd.Timestamp(self.hoje, tz='UTC')
        self.inicio_mes_datetime = pd.Timestamp(self.inicio_mes, tz='UTC')
        self.data_limite_30_dias = self.hoje_datetime - pd.Timedelta(days=30)
    
    def get_performance_metrics(self):
        """
        Calcula métricas de performance usando pandas para análises estatísticas.
        """
        # Dados dos leads
        leads_queryset = Lead.objects.all().values(
            'id', 'status', 'fonte', 'data_criacao', 'responsavel_id'
        )        # Converter para DataFrame do pandas
        leads_df = pd.DataFrame(list(leads_queryset))
        
        if leads_df.empty:
            return self._empty_metrics()
        
        # Converter datas para datetime com timezone aware
        leads_df['data_criacao'] = pd.to_datetime(leads_df['data_criacao'])
        
        # Métricas básicas
        total_leads = len(leads_df)
        leads_convertidos = len(leads_df[leads_df['status'] == 'fechado'])
        taxa_conversao = (leads_convertidos / total_leads * 100) if total_leads > 0 else 0
        
        # Análise temporal - usando apenas a data (sem hora) para comparação
        leads_hoje = len(leads_df[leads_df['data_criacao'].dt.date == self.hoje])
        
        # Análise por origem com pandas
        origem_stats = leads_df.groupby('fonte').agg({
            'id': 'count',
            'status': lambda x: (x == 'fechado').sum()
        }).rename(columns={'id': 'total', 'status': 'convertidos'})
        
        origem_stats['taxa_conversao'] = (
            origem_stats['convertidos'] / origem_stats['total'] * 100
        ).round(2)
          # Tendência dos últimos 30 dias
        ultimos_30_dias = leads_df[
            leads_df['data_criacao'] >= self.data_limite_30_dias
        ]
        
        # Criar range de datas para os últimos 30 dias
        date_range = pd.date_range(
            start=self.hoje - timedelta(days=29),
            end=self.hoje,
            freq='D'
        )
        
        # Agrupar por data e reindexar para preencher datas ausentes
        if not ultimos_30_dias.empty:
            tendencia_diaria = ultimos_30_dias.groupby(
                ultimos_30_dias['data_criacao'].dt.date
            ).size()
            
            # Converter o índice para datetime para compatibilidade
            tendencia_diaria.index = pd.to_datetime(tendencia_diaria.index)
            
            # Reindexar para incluir todas as datas
            tendencia_diaria = tendencia_diaria.reindex(
                date_range.date, fill_value=0
            )
        else:
            # Se não há dados, criar série vazia
            tendencia_diaria = pd.Series(
                0, index=date_range.date
            )
        
        return {
            'total_leads': total_leads,
            'leads_convertidos': leads_convertidos,
            'taxa_conversao': round(taxa_conversao, 2),
            'leads_hoje': leads_hoje,
            'origem_stats': origem_stats.to_dict('index'),
            'tendencia_diaria': {str(k): v for k, v in tendencia_diaria.to_dict().items()},
            'leads_ativos': len(leads_df[~leads_df['status'].isin(['perdido', 'fechado'])])
        }
    
    def get_vendedor_performance(self):
        """
        Análise detalhada de performance por vendedor usando pandas.
        """
        # Dados de vendedores
        vendedores = User.objects.filter(
            is_active=True, 
            profile__role='vendedor'
        ).values('id', 'first_name', 'last_name', 'username')
        
        vendedores_df = pd.DataFrame(list(vendedores))
        
        if vendedores_df.empty:
            return []
        
        # Dados de leads por vendedor
        leads_queryset = Lead.objects.filter(
            responsavel__in=vendedores_df['id']
        ).values('responsavel_id', 'status', 'data_criacao')
        
        leads_df = pd.DataFrame(list(leads_queryset))
        
        # Dados de contatos por vendedor
        contatos_queryset = TentativaContato.objects.filter(
            vendedor__in=vendedores_df['id']
        ).values('vendedor_id', 'resultado', 'data_hora')
        
        contatos_df = pd.DataFrame(list(contatos_queryset))
        
        performance_list = []
        
        for _, vendedor in vendedores_df.iterrows():
            vendedor_id = vendedor['id']
            nome = f"{vendedor['first_name']} {vendedor['last_name']}".strip() or vendedor['username']
            
            # Análise de leads
            vendedor_leads = leads_df[leads_df['responsavel_id'] == vendedor_id] if not leads_df.empty else pd.DataFrame()
            total_leads = len(vendedor_leads)
            leads_convertidos = len(vendedor_leads[vendedor_leads['status'] == 'fechado']) if not vendedor_leads.empty else 0
            taxa_conversao = (leads_convertidos / total_leads * 100) if total_leads > 0 else 0
            
            # Análise de contatos
            vendedor_contatos = contatos_df[contatos_df['vendedor_id'] == vendedor_id] if not contatos_df.empty else pd.DataFrame()
            total_contatos = len(vendedor_contatos)
            contatos_sucesso = len(vendedor_contatos[vendedor_contatos['resultado'] == 'sucesso']) if not vendedor_contatos.empty else 0
            taxa_sucesso_contatos = (contatos_sucesso / total_contatos * 100) if total_contatos > 0 else 0            # Atividade no mês atual
            if not vendedor_leads.empty:
                vendedor_leads['data_criacao'] = pd.to_datetime(vendedor_leads['data_criacao'])
                leads_mes_atual = len(vendedor_leads[
                    vendedor_leads['data_criacao'] >= self.inicio_mes_datetime
                ])
            else:
                leads_mes_atual = 0
            
            if not vendedor_contatos.empty:
                vendedor_contatos['data_hora'] = pd.to_datetime(vendedor_contatos['data_hora'])
                contatos_mes_atual = len(vendedor_contatos[
                    vendedor_contatos['data_hora'] >= self.inicio_mes_datetime
                ])
            else:
                contatos_mes_atual = 0
            
            # Score de performance (algoritmo personalizado)
            score_performance = self._calculate_performance_score(
                taxa_conversao, taxa_sucesso_contatos, total_leads, total_contatos
            )
            
            performance_list.append({
                'vendedor_id': vendedor_id,
                'nome': nome,
                'total_leads': total_leads,
                'leads_convertidos': leads_convertidos,
                'taxa_conversao': round(taxa_conversao, 2),
                'total_contatos': total_contatos,
                'contatos_sucesso': contatos_sucesso,
                'taxa_sucesso_contatos': round(taxa_sucesso_contatos, 2),
                'leads_mes_atual': leads_mes_atual,
                'contatos_mes_atual': contatos_mes_atual,
                'score_performance': round(score_performance, 2)
            })
        
        # Ordenar por score de performance
        return sorted(performance_list, key=lambda x: x['score_performance'], reverse=True)
    
    def get_funil_vendas_analysis(self):
        """
        Análise do funil de vendas com cálculo de taxa de conversão entre etapas.
        """
        status_order = ['novo', 'contatado', 'qualificado', 'proposta', 'negociacao', 'fechado']
        status_cores = {
            'novo': '#FFD700',
            'contatado': '#87CEEB', 
            'qualificado': '#32CD32',
            'proposta': '#FF8C00',
            'negociacao': '#9370DB',
            'fechado': '#228B22',
            'perdido': '#DC143C'
        }
        
        # Dados do funil
        funil_data = Lead.objects.values('status').annotate(
            count=Count('id')
        )
        
        funil_dict = {item['status']: item['count'] for item in funil_data}
        
        funil_analysis = []
        for i, status in enumerate(status_order):
            count = funil_dict.get(status, 0)
            
            # Calcular taxa de conversão para a próxima etapa
            if i < len(status_order) - 1:
                proximo_status = status_order[i + 1]
                total_atual_e_seguintes = sum(
                    funil_dict.get(s, 0) for s in status_order[i:]
                )
                taxa_conversao_proxima = (
                    funil_dict.get(proximo_status, 0) / total_atual_e_seguintes * 100
                ) if total_atual_e_seguintes > 0 else 0
            else:
                taxa_conversao_proxima = 0
            
            funil_analysis.append({
                'status': status.replace('_', ' ').title(),
                'count': count,
                'cor': status_cores.get(status, '#808080'),
                'taxa_conversao_proxima': round(taxa_conversao_proxima, 2)
            })
        
        return funil_analysis
    
    def get_real_time_activity(self):
        """
        Análise de atividade em tempo real (últimas 24 horas).
        """
        agora = timezone.now()
        inicio_24h = agora - timedelta(hours=24)
        
        # Contatos por hora
        contatos_24h = TentativaContato.objects.filter(
            data_hora__gte=inicio_24h
        ).values('data_hora')
        
        contatos_df = pd.DataFrame(list(contatos_24h))
        
        if contatos_df.empty:
            # Retornar dados vazios para as últimas 24 horas
            return [
                {'hora': (agora - timedelta(hours=i)).strftime('%H:00'), 'count': 0}
                for i in range(23, -1, -1)
            ]
        
        contatos_df['data_hora'] = pd.to_datetime(contatos_df['data_hora'])
        contatos_df['hora'] = contatos_df['data_hora'].dt.hour
        
        # Agrupar por hora
        contatos_por_hora = contatos_df.groupby('hora').size()
        
        # Preparar dados para as últimas 24 horas
        atividade_24h = []
        for i in range(23, -1, -1):
            hora_atual = agora - timedelta(hours=i)
            hora_num = hora_atual.hour
            count = contatos_por_hora.get(hora_num, 0)
            
            atividade_24h.append({
                'hora': hora_atual.strftime('%H:00'),
                'count': count
            })
        
        return atividade_24h
    
    def get_predictive_insights(self):
        """
        Insights preditivos baseados em análise de tendências.
        """
        # Análise de tendência dos últimos 30 dias
        ultimos_30_dias = []
        for i in range(29, -1, -1):
            dia = self.hoje - timedelta(days=i)
            leads_dia = Lead.objects.filter(data_criacao__date=dia).count()
            ultimos_30_dias.append(leads_dia)
        
        # Usar pandas para análise de tendência
        series_leads = pd.Series(ultimos_30_dias)
        
        # Cálculo de tendência (regressão linear simples)
        x = np.arange(len(series_leads))
        coeficientes = np.polyfit(x, series_leads, 1)
        tendencia_diaria = coeficientes[0]  # Slope da linha de tendência
        
        # Previsão para os próximos 7 dias
        previsao_7_dias = []
        for i in range(1, 8):
            previsao = max(0, int(series_leads.iloc[-1] + (tendencia_diaria * i)))
            previsao_7_dias.append(previsao)
        
        # Análise de sazonalidade (dia da semana)
        dados_sazonalidade = []
        for dia_semana in range(7):  # 0 = segunda, 6 = domingo
            leads_dia_semana = Lead.objects.filter(
                data_criacao__week_day=dia_semana + 2  # Django usa 1=domingo
            ).count()
            dados_sazonalidade.append(leads_dia_semana)
        
        return {
            'tendencia_diaria': round(tendencia_diaria, 2),
            'previsao_7_dias': previsao_7_dias,
            'media_30_dias': round(series_leads.mean(), 2),
            'desvio_padrao': round(series_leads.std(), 2),
            'sazonalidade_semanal': dados_sazonalidade
        }
    
    def _calculate_performance_score(self, taxa_conversao, taxa_sucesso_contatos, total_leads, total_contatos):
        """
        Algoritmo personalizado para calcular score de performance.
        """
        # Pesos para diferentes métricas
        peso_conversao = 0.4
        peso_sucesso_contatos = 0.3
        peso_volume_leads = 0.2
        peso_volume_contatos = 0.1
        
        # Normalizar volumes (logarítmico para evitar domínio de valores muito altos)
        volume_leads_normalizado = min(100, np.log1p(total_leads) * 10)
        volume_contatos_normalizado = min(100, np.log1p(total_contatos) * 5)
        
        # Calcular score final
        score = (
            taxa_conversao * peso_conversao +
            taxa_sucesso_contatos * peso_sucesso_contatos +
            volume_leads_normalizado * peso_volume_leads +
            volume_contatos_normalizado * peso_volume_contatos
        )
        
        return min(100, score)  # Limitar a 100
    
    def _empty_metrics(self):
        """Retorna métricas vazias quando não há dados."""
        return {
            'total_leads': 0,
            'leads_convertidos': 0,
            'taxa_conversao': 0,
            'leads_hoje': 0,
            'origem_stats': {},
            'tendencia_diaria': {},
            'leads_ativos': 0
        }


class ReportGenerator:
    """Gerador de relatórios usando pandas para análises avançadas."""
    
    def __init__(self):
        self.analytics = DashboardAnalytics()
    
    def generate_performance_summary(self, periodo_dias=30):
        """
        Gera um resumo de performance para um período específico.
        """
        inicio_periodo = timezone.now().date() - timedelta(days=periodo_dias)
        
        # Dados do período
        leads_periodo = Lead.objects.filter(
            data_criacao__date__gte=inicio_periodo
        ).values('status', 'fonte', 'responsavel_id', 'data_criacao')
        
        if not leads_periodo:
            return None
        
        leads_df = pd.DataFrame(list(leads_periodo))
        leads_df['data_criacao'] = pd.to_datetime(leads_df['data_criacao'])
        
        # Análises do período
        summary = {
            'periodo': f"Últimos {periodo_dias} dias",
            'total_leads': len(leads_df),
            'leads_convertidos': len(leads_df[leads_df['status'] == 'fechado']),
            'origem_mais_efetiva': self._get_origem_mais_efetiva(leads_df),
            'vendedor_destaque': self._get_vendedor_destaque(leads_df),
            'tendencia_periodo': self._get_tendencia_periodo(leads_df),
        }
        
        return summary
    
    def _get_origem_mais_efetiva(self, leads_df):
        """Identifica a origem mais efetiva."""
        if leads_df.empty:
            return None
        
        origem_stats = leads_df.groupby('fonte').agg({
            'status': lambda x: (x == 'fechado').sum() / len(x) * 100
        }).round(2)
        
        if not origem_stats.empty:
            melhor_origem = origem_stats['status'].idxmax()
            taxa = origem_stats['status'].max()
            return {'origem': melhor_origem, 'taxa_conversao': taxa}
        
        return None
    
    def _get_vendedor_destaque(self, leads_df):
        """Identifica o vendedor com melhor performance."""
        if leads_df.empty or 'responsavel_id' not in leads_df.columns:
            return None
        
        vendedor_stats = leads_df.groupby('responsavel_id').agg({
            'status': lambda x: (x == 'fechado').sum() / len(x) * 100
        }).round(2)
        
        if not vendedor_stats.empty:
            melhor_vendedor_id = vendedor_stats['status'].idxmax()
            taxa = vendedor_stats['status'].max()
            
            try:
                vendedor = User.objects.get(id=melhor_vendedor_id)
                nome = f"{vendedor.first_name} {vendedor.last_name}".strip() or vendedor.username
                return {'vendedor': nome, 'taxa_conversao': taxa}
            except User.DoesNotExist:
                pass
        
        return None
    
    def _get_tendencia_periodo(self, leads_df):
        """Calcula a tendência do período."""
        if leads_df.empty:
            return 0
        
        # Agrupar por dia
        leads_por_dia = leads_df.groupby(leads_df['data_criacao'].dt.date).size()
        
        if len(leads_por_dia) < 2:
            return 0
        
        # Calcular tendência
        x = np.arange(len(leads_por_dia))
        coeficientes = np.polyfit(x, leads_por_dia.values, 1)
        
        return round(coeficientes[0], 2)
