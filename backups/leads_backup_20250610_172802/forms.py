from django import forms
from .models import Lead, TemplateWhatsApp, TemplateEmail, HistoricoContato

# Formulários de comunicação
class EnviarWhatsAppForm(forms.Form):
    """Formulário para enviar mensagens de WhatsApp."""
    template = forms.ModelChoiceField(
        queryset=TemplateWhatsApp.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select mb-2', 'id': 'template-whatsapp'})
    )
    mensagem = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 6, 
            'placeholder': 'Digite sua mensagem de WhatsApp aqui...',
            'id': 'mensagem-whatsapp'
        }),
    )
    
    def clean(self):
        cleaned_data = super().clean()
        template = cleaned_data.get('template')
        mensagem = cleaned_data.get('mensagem')
        
        if not mensagem and not template:
            raise forms.ValidationError("Selecione um template ou digite uma mensagem.")
        
        return cleaned_data


class EnviarEmailForm(forms.Form):
    """Formulário para enviar e-mails."""
    template = forms.ModelChoiceField(
        queryset=TemplateEmail.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select mb-2', 'id': 'template-email'})
    )
    assunto = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'id': 'assunto-email'})
    )
    mensagem = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'id': 'mensagem-email'
        }),
    )
    
    def clean(self):
        cleaned_data = super().clean()
        assunto = cleaned_data.get('assunto')
        mensagem = cleaned_data.get('mensagem')
        
        if not assunto:
            raise forms.ValidationError("O assunto do e-mail é obrigatório.")
        
        if not mensagem:
            raise forms.ValidationError("A mensagem do e-mail é obrigatória.")
        
        return cleaned_data


class NovoTemplateForm(forms.ModelForm):
    """Formulário base para criação de templates."""
    class Meta:
        fields = ['nome', 'conteudo', 'pode_personalizar']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'pode_personalizar': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class TemplateWhatsAppForm(NovoTemplateForm):
    """Formulário para templates de WhatsApp."""
    class Meta(NovoTemplateForm.Meta):
        model = TemplateWhatsApp


class TemplateEmailForm(NovoTemplateForm):
    """Formulário para templates de e-mail."""
    assunto = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta(NovoTemplateForm.Meta):
        model = TemplateEmail
        fields = ['nome', 'assunto', 'conteudo', 'pode_personalizar']


# Formulários de Leads
class QuickLeadForm(forms.ModelForm):
    """Formulário para cadastro rápido de leads."""
    
    class Meta:
        model = Lead
        fields = [
            'nome', 'telefone', 'whatsapp', 'email', 'empresa',
            'interesse', 'valor_interesse', 'prioridade', 'fonte', 'observacoes'
        ]
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do cliente'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da empresa (se aplicável)'}),
            'interesse': forms.Select(attrs={'class': 'form-select'}),
            'valor_interesse': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'R$ 0,00'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'fonte': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações importantes sobre este lead'})
        }
        
class LeadFilterForm(forms.Form):
    """Formulário para filtrar leads no painel principal."""
    STATUS_CHOICES = [('', 'Todos')] + Lead.STATUS_CHOICES
    INTEREST_CHOICES = [('', 'Todos')] + Lead.INTEREST_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    interesse = forms.ChoiceField(
        choices=INTEREST_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    prioridade = forms.ChoiceField(
        choices=[('', 'Todas'), (1, 'Baixa'), (2, 'Média'), (3, 'Alta')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome, empresa, telefone...'
        })
    )


class AdvancedSearchForm(forms.Form):
    """Formulário de busca avançada para leads."""
    SEARCH_FIELDS = [
        ('nome', 'Nome'),
        ('telefone', 'Telefone/WhatsApp'),
        ('email', 'Email'),
        ('empresa', 'Empresa'),
    ]
    
    campo_busca = forms.ChoiceField(
        choices=SEARCH_FIELDS,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Campo de busca'
        })
    )
    
    valor_busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o valor para buscar...',
            'aria-label': 'Valor de busca'
        })
    )
    
    per_page = forms.ChoiceField(
        choices=[(10, '10'), (25, '25'), (50, '50'), (100, '100')],
        initial=10,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'aria-label': 'Itens por página'
        })
    )
