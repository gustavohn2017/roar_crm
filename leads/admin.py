"""
Arquivo consolidado para administração do app leads.
"""

from django.contrib import admin
from .models import Lead, TemplateComunitacao, HistoricoContato

@admin.register(TemplateComunitacao)
class TemplateComunitacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'assunto', 'ativo', 'criado_em')
    list_filter = ('tipo', 'ativo')
    search_fields = ('nome', 'conteudo', 'assunto')
    date_hierarchy = 'criado_em'

@admin.register(HistoricoContato)
class HistoricoContatoAdmin(admin.ModelAdmin):
    list_display = ('lead', 'tipo', 'assunto', 'status', 'data_envio')
    list_filter = ('tipo', 'status')
    search_fields = ('lead__nome', 'assunto', 'mensagem')
    date_hierarchy = 'data_envio'

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'telefone', 'email', 'status', 'interesse', 'prioridade', 'data_criacao')
    list_filter = ('status', 'interesse', 'prioridade', 'fonte')
    search_fields = ('nome', 'empresa', 'email', 'telefone', 'whatsapp', 'cpf_cnpj')
    date_hierarchy = 'data_criacao'
    readonly_fields = ('data_criacao', 'data_modificacao')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'cpf_cnpj', 'email', 'telefone', 'whatsapp')
        }),
        ('Informações Empresariais', {
            'fields': ('empresa', 'cargo', 'faturamento_mensal')
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Informações de Negócio', {
            'fields': ('interesse', 'valor_interesse', 'prazo_desejado')
        }),
        ('Gestão', {
            'fields': ('status', 'fonte', 'responsavel', 'prioridade', 'observacoes')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_modificacao', 'data_ultimo_contato', 'data_proxima_acao')
        }),
    )
