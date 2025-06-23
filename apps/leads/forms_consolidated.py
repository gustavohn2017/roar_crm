"""
Formulários consolidados para gestão de leads.
"""

from django import forms
from django.db.models import Q
from apps.leads.models_consolidated import Lead, TemplateComunitacao, HistoricoContato


class LeadForm(forms.ModelForm):
    """Formulário principal para cadastro e edição de leads."""
    
    class Meta:
        model = Lead
        fields = [
            'nome', 'cpf_cnpj', 'email', 'telefone', 'whatsapp',
            'empresa', 'cargo', 'faturamento_mensal',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'interesse', 'valor_interesse', 'prazo_desejado',
            'status', 'fonte', 'prioridade', 'observacoes'
        ]
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da empresa'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo/Função'}),
            'faturamento_mensal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'interesse': forms.Select(attrs={'class': 'form-select'}),
            'valor_interesse': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'prazo_desejado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Meses'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'fonte': forms.Select(attrs={'class': 'form-select'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class QuickLeadForm(forms.ModelForm):
    """Formulário simplificado para cadastro rápido de leads."""
    
    is_whatsapp = forms.BooleanField(
        label='O telefone também é WhatsApp',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Lead
        fields = [
            'nome', 'telefone', 'email', 'empresa',
            'interesse', 'valor_interesse', 'prioridade', 'fonte', 'observacoes'
        ]
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do cliente'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Empresa (opcional)'}),
            'interesse': forms.Select(attrs={'class': 'form-select'}),
            'valor_interesse': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor de interesse'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'fonte': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observações'}),
        }
    
    def save(self, commit=True):
        lead = super().save(commit=False)
        
        # Se marcou que o telefone é WhatsApp, copia o valor
        if self.cleaned_data.get('is_whatsapp'):
            lead.whatsapp = lead.telefone
        
        if commit:
            lead.save()
        
        return lead


class LeadFilterForm(forms.Form):
    """Formulário para filtros na listagem de leads."""
    
    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome, empresa, telefone ou email...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Lead.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    interesse = forms.ChoiceField(
        choices=[('', 'Todos os interesses')] + Lead.INTEREST_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    prioridade = forms.ChoiceField(
        choices=[('', 'Todas as prioridades')] + Lead.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fonte = forms.ChoiceField(
        choices=[('', 'Todas as fontes')] + Lead.SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class AdvancedSearchForm(forms.Form):
    """Formulário para busca avançada de leads."""
    
    CAMPO_CHOICES = [
        ('nome', 'Nome'),
        ('telefone', 'Telefone/WhatsApp'),
        ('email', 'E-mail'),
        ('empresa', 'Empresa'),
    ]
    
    campo_busca = forms.ChoiceField(
        choices=CAMPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    valor_busca = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o valor para busca'})
    )


class TemplateForm(forms.ModelForm):
    """Formulário para templates de comunicação."""
    
    class Meta:
        model = TemplateComunitacao
        fields = ['nome', 'tipo', 'assunto', 'conteudo', 'ativo']
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ContatoForm(forms.ModelForm):
    """Formulário para registro de contatos."""
    
    class Meta:
        model = HistoricoContato
        fields = ['tipo', 'assunto', 'mensagem', 'template_usado']
        
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'template_usado': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        tipo_contato = kwargs.pop('tipo_contato', None)
        super().__init__(*args, **kwargs)
        
        if tipo_contato:
            self.fields['template_usado'].queryset = TemplateComunitacao.objects.filter(
                tipo=tipo_contato, ativo=True
            )
        else:
            self.fields['template_usado'].queryset = TemplateComunitacao.objects.filter(ativo=True)
