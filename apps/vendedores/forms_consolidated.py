"""
Formulários consolidados para a aplicação vendedores.
Inclui formulários para TentativaContato, Evento e Nota.
"""
from django import forms
from .models import TentativaContato, Evento, Nota


class TentativaContatoForm(forms.ModelForm):
    """Formulário para registrar tentativas de contato."""
    
    class Meta:
        model = TentativaContato
        fields = ['resultado', 'observacoes']
        widgets = {
            'resultado': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'observacoes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Detalhes sobre a tentativa de contato...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['observacoes'].required = False


class EventoForm(forms.ModelForm):
    """Formulário para criar e editar eventos."""
    
    class Meta:
        model = Evento
        fields = ['titulo', 'descricao', 'data', 'hora', 'tipo', 'lead']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do evento',
                'required': True
            }),
            'descricao': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descrição detalhada do evento...'
            }),
            'data': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'hora': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'required': True
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'lead': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        vendedor = kwargs.pop('vendedor', None)
        super().__init__(*args, **kwargs)
        
        if vendedor:
            # Filtrar leads disponíveis para o vendedor
            from apps.leads.models_consolidated import Lead
            self.fields['lead'].queryset = Lead.objects.filter(
                status__in=['novo', 'contatado', 'qualificado']
            ).order_by('nome')
        
        self.fields['lead'].required = False
        self.fields['lead'].empty_label = "Nenhum lead associado"


class NotaForm(forms.ModelForm):
    """Formulário para criar e editar notas e lembretes."""
    
    class Meta:
        model = Nota
        fields = ['titulo', 'conteudo', 'prioridade', 'tipo', 'lead']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título da nota/lembrete',
                'required': True
            }),
            'conteudo': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Conteúdo da nota...',
                'required': True
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'lead': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        vendedor = kwargs.pop('vendedor', None)
        super().__init__(*args, **kwargs)
        
        if vendedor:
            # Filtrar leads disponíveis para o vendedor
            from apps.leads.models_consolidated import Lead
            self.fields['lead'].queryset = Lead.objects.filter(
                status__in=['novo', 'contatado', 'qualificado']
            ).order_by('nome')
        
        self.fields['lead'].required = False
        self.fields['lead'].empty_label = "Nenhum lead associado"
        self.fields['tipo'].initial = 'nota'


class QuickEventoForm(forms.ModelForm):
    """Formulário simplificado para criação rápida de eventos."""
    
    class Meta:
        model = Evento
        fields = ['titulo', 'data', 'hora', 'tipo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Título do evento'
            }),
            'data': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control form-control-sm'
            }),
            'hora': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control form-control-sm'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
        }


class QuickNotaForm(forms.ModelForm):
    """Formulário simplificado para criação rápida de notas."""
    
    class Meta:
        model = Nota
        fields = ['titulo', 'conteudo', 'tipo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Título da nota'
            }),
            'conteudo': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control form-control-sm',
                'placeholder': 'Conteúdo...'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].initial = 'nota'


# Formulários de filtro para dashboard
class EventoFilterForm(forms.Form):
    """Formulário para filtros de eventos no dashboard."""
    
    PERIODO_CHOICES = [
        ('hoje', 'Hoje'),
        ('semana', 'Esta semana'),
        ('mes', 'Este mês'),
        ('todos', 'Todos'),
    ]
    
    STATUS_CHOICES = [
        ('pendentes', 'Pendentes'),
        ('concluidos', 'Concluídos'),
        ('atrasados', 'Atrasados'),
        ('todos', 'Todos'),
    ]
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        required=False,
        initial='semana',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        initial='pendentes',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    tipo = forms.ChoiceField(
        choices=[('todos', 'Todos')] + Evento.TIPOS_EVENTO,
        required=False,
        initial='todos',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )


class NotaFilterForm(forms.Form):
    """Formulário para filtros de notas no dashboard."""
    
    STATUS_CHOICES = [
        ('ativas', 'Ativas'),
        ('concluidas', 'Concluídas'),
        ('todas', 'Todas'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        initial='ativas',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    tipo = forms.ChoiceField(
        choices=[('todos', 'Todos')] + Nota.TIPO_CHOICES,
        required=False,
        initial='todos',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    prioridade = forms.ChoiceField(
        choices=[('todas', 'Todas')] + Nota.PRIORIDADE_CHOICES,
        required=False,
        initial='todas',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
