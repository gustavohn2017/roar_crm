"""
O painel administrativo do Django foi desativado para a maioria das operações.
No entanto, alguns modelos específicos ainda são gerenciados através do admin para facilitar.
"""

from django.contrib import admin
from .models import TemplateComunitacao, HistoricoContato

@admin.register(TemplateWhatsApp)
class TemplateWhatsAppAdmin(admin.ModelAdmin):
    list_display = ('nome', 'conteudo', 'pode_personalizar', 'data_criacao')
    list_filter = ('pode_personalizar',)
    search_fields = ('nome', 'conteudo')
    date_hierarchy = 'data_criacao'

@admin.register(TemplateEmail)
class TemplateEmailAdmin(admin.ModelAdmin):
    list_display = ('nome', 'assunto', 'pode_personalizar', 'data_criacao')
    list_filter = ('pode_personalizar',)
    search_fields = ('nome', 'assunto', 'conteudo_html', 'conteudo_texto')
    date_hierarchy = 'data_criacao'
    
@admin.register(HistoricoContato)
class HistoricoContatoAdmin(admin.ModelAdmin):
    list_display = ('lead', 'tipo', 'data', 'responsavel', 'foi_respondido')
    list_filter = ('tipo', 'foi_respondido')
    search_fields = ('lead__nome', 'conteudo')
    date_hierarchy = 'data'
