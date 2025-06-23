from django.contrib import admin
from .models import (
    LeadScore, Workflow, AcaoWorkflow, CampanhaNutricao,
    EtapaCampanha, GatilhoAutomatico, ExecucaoWorkflow,
    HistoricoAutomacao, ParticipacaoCampanha, CriterioScore
)

@admin.register(LeadScore)
class LeadScoreAdmin(admin.ModelAdmin):
    list_display = ('lead', 'pontuacao_total', 'pontos_demograficos', 'pontos_comportamentais', 
                    'pontos_engajamento', 'pontos_interesse', 'ultima_atualizacao')
    list_filter = ('ultima_atualizacao', 'classificacao')
    search_fields = ('lead__nome', 'lead__email', 'lead__empresa')
    readonly_fields = ('ultima_atualizacao',)
    ordering = ('-pontuacao_total',)
    
    fieldsets = (
        ('Lead', {
            'fields': ('lead',)
        }),
        ('Scores', {
            'fields': ('pontos_demograficos', 'pontos_comportamentais', 
                      'pontos_engajamento', 'pontos_interesse', 'pontuacao_total', 'classificacao')
        }),        ('Timestamps', {
            'fields': ('ultima_atualizacao',),
            'classes': ('collapse',)
        })
    )

@admin.register(CriterioScore)
class CriterioScoreAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'pontos', 'ativo', 'data_criacao')
    list_filter = ('tipo', 'ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('data_criacao',)
    ordering = ('tipo', 'nome')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo', 'descricao', 'ativo')
        }),
        ('Configurações', {
            'fields': ('pontos', 'condicao')
        }),
        ('Timestamps', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        })
    )

class AcaoWorkflowInline(admin.TabularInline):
    model = AcaoWorkflow
    extra = 1
    fields = ('ordem', 'tipo_acao', 'parametros', 'delay_dias')

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('nome', 'trigger', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'trigger', 'data_criacao')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('data_criacao',)
    # Temporarily disabled due to model conflicts
    # inlines = [AcaoWorkflowInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ativo', 'criado_por')
        }),
        ('Configurações do Gatilho', {
            'fields': ('trigger', 'condicoes')
        }),
        ('Timestamps', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        })
    )

@admin.register(AcaoWorkflow)
class AcaoWorkflowAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'ordem', 'tipo_acao', 'delay_dias')
    list_filter = ('tipo_acao', 'workflow')
    search_fields = ('workflow__nome', 'parametros')
    ordering = ('workflow', 'ordem')

class EtapaCampanhaInline(admin.TabularInline):
    model = EtapaCampanha
    extra = 1
    fields = ('ordem', 'nome', 'tipo', 'delay_dias')

@admin.register(CampanhaNutricao)
class CampanhaNutricaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'data_inicio', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('data_criacao',)
    # Temporarily disabled due to model conflicts
    # inlines = [EtapaCampanhaInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'objetivo', 'status', 'criado_por')
        }),
        ('Configurações', {
            'fields': ('data_inicio', 'data_fim', 'criterios_segmentacao')
        }),
        ('Timestamps', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        })
    )

@admin.register(EtapaCampanha)
class EtapaCampanhaAdmin(admin.ModelAdmin):
    list_display = ('campanha', 'ordem', 'nome', 'tipo', 'delay_dias')
    list_filter = ('tipo', 'campanha')
    search_fields = ('campanha__nome', 'nome', 'conteudo')
    ordering = ('campanha', 'ordem')

@admin.register(GatilhoAutomatico)
class GatilhoAutomaticoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'evento', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'evento', 'data_criacao')
    search_fields = ('nome',)
    readonly_fields = ('data_criacao',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'ativo')
        }),
        ('Configurações do Evento', {
            'fields': ('evento', 'condicoes', 'workflow')
        }),
        ('Timestamps', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        })
    )

@admin.register(ExecucaoWorkflow)
class ExecucaoWorkflowAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'lead', 'status', 'acao_atual', 'data_inicio', 'data_conclusao')
    list_filter = ('status', 'data_inicio', 'workflow')
    search_fields = ('workflow__nome', 'lead__nome', 'lead__email')
    readonly_fields = ('data_inicio', 'data_conclusao')
    ordering = ('-data_inicio',)
    
    fieldsets = (
        ('Execução', {
            'fields': ('workflow', 'lead', 'status', 'acao_atual')
        }),
        ('Resultados', {
            'fields': ('log_execucao', 'erro_detalhes')
        }),
        ('Timestamps', {
            'fields': ('data_inicio', 'data_conclusao', 'data_proxima_acao'),
            'classes': ('collapse',)
        })
    )

@admin.register(HistoricoAutomacao)
class HistoricoAutomacaoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'lead', 'acao', 'sucesso', 'data_execucao')
    list_filter = ('tipo', 'sucesso', 'data_execucao')
    search_fields = ('lead__nome', 'lead__email', 'detalhes')
    readonly_fields = ('data_execucao',)
    ordering = ('-data_execucao',)
    
    fieldsets = (
        ('Execução', {
            'fields': ('tipo', 'lead', 'acao', 'sucesso')
        }),
        ('Detalhes', {
            'fields': ('detalhes',)
        }),
        ('Referências', {
            'fields': ('workflow', 'campanha', 'gatilho'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('data_execucao',)
        })
    )

@admin.register(ParticipacaoCampanha)
class ParticipacaoCampanhaAdmin(admin.ModelAdmin):
    list_display = ('campanha', 'lead', 'etapa_atual', 'status', 'data_entrada')
    list_filter = ('status', 'data_entrada', 'campanha')
    search_fields = ('campanha__nome', 'lead__nome', 'lead__email')
    readonly_fields = ('data_entrada', 'data_conclusao')
    ordering = ('-data_entrada',)
    
    fieldsets = (
        ('Inscrição', {
            'fields': ('campanha', 'lead', 'status')
        }),
        ('Progresso', {
            'fields': ('etapa_atual', 'data_proxima_etapa')
        }),
        ('Timestamps', {
            'fields': ('data_entrada', 'data_conclusao'),
            'classes': ('collapse',)
        })
    )

# Configurações do admin
admin.site.site_header = 'Lions CRM - Automação'
admin.site.site_title = 'Automação'
admin.site.index_title = 'Administração da Automação'
