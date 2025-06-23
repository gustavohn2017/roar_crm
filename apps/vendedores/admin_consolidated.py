"""
Configuração do admin para a aplicação vendedores consolidada.
"""
from django.contrib import admin
from .models import TentativaContato, Evento, Nota


@admin.register(TentativaContato)
class TentativaContatoAdmin(admin.ModelAdmin):
    """Admin para tentativas de contato."""
    
    list_display = ['lead', 'vendedor', 'data_hora', 'resultado', 'observacoes_truncadas']
    list_filter = ['resultado', 'data_hora', 'vendedor']
    search_fields = ['lead__nome', 'lead__email', 'vendedor__username', 'observacoes']
    date_hierarchy = 'data_hora'
    ordering = ['-data_hora']
    readonly_fields = ['data_hora']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('lead', 'vendedor', 'data_hora')
        }),
        ('Resultado do Contato', {
            'fields': ('resultado', 'observacoes')
        }),
    )
    
    def observacoes_truncadas(self, obj):
        """Exibe observações truncadas na lista."""
        if obj.observacoes:
            return obj.observacoes[:50] + '...' if len(obj.observacoes) > 50 else obj.observacoes
        return '-'
    observacoes_truncadas.short_description = 'Observações'
    
    def get_queryset(self, request):
        """Otimiza consultas com select_related."""
        return super().get_queryset(request).select_related('lead', 'vendedor')


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    """Admin para eventos."""
    
    list_display = ['titulo', 'vendedor', 'data', 'hora', 'tipo', 'concluido', 'lead_associado']
    list_filter = ['tipo', 'concluido', 'data', 'vendedor']
    search_fields = ['titulo', 'descricao', 'vendedor__username', 'lead__nome']
    date_hierarchy = 'data'
    ordering = ['data', 'hora']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'vendedor')
        }),
        ('Agendamento', {
            'fields': ('data', 'hora', 'tipo')
        }),
        ('Associações', {
            'fields': ('lead', 'concluido')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ['collapse']
        }),
    )
    
    def lead_associado(self, obj):
        """Exibe lead associado ou '-'."""
        return obj.lead.nome if obj.lead else '-'
    lead_associado.short_description = 'Lead'
    
    def get_queryset(self, request):
        """Otimiza consultas com select_related."""
        return super().get_queryset(request).select_related('vendedor', 'lead')


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    """Admin para notas."""
    
    list_display = ['titulo', 'vendedor', 'tipo', 'prioridade', 'concluido', 'data_criacao', 'lead_associado']
    list_filter = ['tipo', 'prioridade', 'concluido', 'data_criacao', 'vendedor']
    search_fields = ['titulo', 'conteudo', 'vendedor__username', 'lead__nome']
    date_hierarchy = 'data_criacao'
    ordering = ['-prioridade', '-data_criacao']
    readonly_fields = ['data_criacao', 'data_atualizacao', 'data_conclusao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'conteudo', 'vendedor')
        }),
        ('Configurações', {
            'fields': ('tipo', 'prioridade', 'concluido')
        }),
        ('Associações', {
            'fields': ('lead',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'data_conclusao'),
            'classes': ['collapse']
        }),
    )
    
    def lead_associado(self, obj):
        """Exibe lead associado ou '-'."""
        return obj.lead.nome if obj.lead else '-'
    lead_associado.short_description = 'Lead'
    
    def get_queryset(self, request):
        """Otimiza consultas com select_related."""
        return super().get_queryset(request).select_related('vendedor', 'lead')


# Configurações adicionais do admin
admin.site.site_header = "ROAR CRM - Administração"
admin.site.site_title = "ROAR CRM Admin"
admin.site.index_title = "Bem-vindo ao painel administrativo do ROAR CRM"
