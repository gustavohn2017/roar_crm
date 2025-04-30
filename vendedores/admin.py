from django.contrib import admin
from .models import TentativaContato


@admin.register(TentativaContato)
class TentativaContatoAdmin(admin.ModelAdmin):
    list_display = ('lead', 'vendedor', 'data_hora', 'resultado')
    list_filter = ('resultado', 'vendedor', 'data_hora')
    search_fields = ('lead__nome', 'lead__email', 'vendedor__username', 'observacoes')
    date_hierarchy = 'data_hora'