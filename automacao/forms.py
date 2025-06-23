"""
Formulários para o sistema de automação.
"""
from django import forms
from django.contrib.auth.models import User
from leads.models import Lead, TemplateComunitacao
from .models import (
    Workflow, AcaoWorkflow, CampanhaNutricao, EtapaCampanha,
    GatilhoAutomatico, CriterioScore
)


class WorkflowForm(forms.ModelForm):
    """
    Formulário para criação e edição de workflows.
    """
    class Meta:
        model = Workflow
        fields = ['nome', 'descricao', 'trigger', 'condicoes', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do workflow'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do workflow'
            }),
            'trigger': forms.Select(attrs={'class': 'form-select'}),
            'condicoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Condições em formato JSON (opcional)'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condicoes'].help_text = (
            'Exemplo: {"status_requerido": "novo", "score_minimo": 30}'
        )


class AcaoWorkflowForm(forms.ModelForm):
    """
    Formulário para adicionar ações a workflows.
    """
    
    template_email = forms.ModelChoiceField(
        queryset=TemplateComunitacao.objects.filter(tipo='email'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Selecione um template (opcional)"
    )
    
    template_whatsapp = forms.ModelChoiceField(
        queryset=TemplateComunitacao.objects.filter(tipo='whatsapp'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Selecione um template (opcional)"
    )
    
    vendedor_responsavel = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role__in=['vendedor', 'supervisor']),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Selecione um vendedor (opcional)"
    )
    
    class Meta:
        model = AcaoWorkflow
        fields = [
            'tipo_acao', 'delay_dias', 'parametros', 'condicoes'
        ]
        widgets = {
            'tipo_acao': forms.Select(attrs={'class': 'form-select'}),
            'delay_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),
            'parametros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Parâmetros em formato JSON'
            }),
            'condicoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Condições específicas (opcional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parametros'].help_text = (
            'Exemplo para e-mail: '
            '{"assunto": "Bem-vindo!", "corpo": "Olá {nome}..."}'
        )


class CampanhaNutricaoForm(forms.ModelForm):
    """
    Formulário para campanhas de nutrição.
    """
    class Meta:
        model = CampanhaNutricao
        fields = [
            'nome', 'descricao', 'objetivo', 'status',
            'data_inicio', 'data_fim', 'criterios_segmentacao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da campanha'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da campanha'
            }),
            'objetivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objetivo principal da campanha'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'data_fim': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'criterios_segmentacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Critérios de segmentação em JSON'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['criterios_segmentacao'].help_text = (
            'Exemplo: {"status": ["novo", "contatado"], "score_minimo": 30}'
        )


class EtapaCampanhaForm(forms.ModelForm):
    """
    Formulário para etapas de campanhas.
    """
    class Meta:
        model = EtapaCampanha
        fields = [
            'nome', 'tipo', 'delay_dias', 'assunto', 'conteudo',
            'template', 'template_whatsapp', 'condicoes'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da etapa'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'delay_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 1
            }),
            'assunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assunto (para e-mails)'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Conteúdo da mensagem'
            }),
            'template': forms.Select(attrs={'class': 'form-select'}),
            'template_whatsapp': forms.Select(attrs={'class': 'form-select'}),            'condicoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Condições para executar esta etapa'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = TemplateComunitacao.objects.filter(tipo='email')
        self.fields['template_whatsapp'].queryset = TemplateComunitacao.objects.filter(tipo='whatsapp')
        self.fields['template'].empty_label = "Selecione um template (opcional)"
        self.fields['template_whatsapp'].empty_label = "Selecione um template (opcional)"


class GatilhoAutomaticoForm(forms.ModelForm):
    """
    Formulário para gatilhos automáticos.
    """
    class Meta:
        model = GatilhoAutomatico
        fields = ['nome', 'evento', 'condicoes', 'workflow', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do gatilho'
            }),
            'evento': forms.Select(attrs={'class': 'form-select'}),
            'condicoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Condições em formato JSON'
            }),
            'workflow': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['workflow'].queryset = Workflow.objects.filter(ativo=True)


class CriterioScoreForm(forms.ModelForm):
    """
    Formulário para critérios de pontuação.
    """
    class Meta:
        model = CriterioScore
        fields = ['nome', 'tipo', 'descricao', 'pontos', 'condicao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do critério'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do critério'
            }),
            'pontos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': -50,
                'max': 50
            }),
            'condicao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Condição em formato JSON'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class FiltroLeadsForm(forms.Form):
    """
    Formulário para filtrar leads para workflows e campanhas.
    """
    STATUS_CHOICES = [('', 'Todos os status')] + Lead.STATUS_CHOICES
    INTERESSE_CHOICES = [('', 'Todos os interesses')] + Lead.INTEREST_CHOICES
    SCORE_CHOICES = [
        ('', 'Todos os scores'),
        ('frio', 'Lead Frio (0-30)'),
        ('morno', 'Lead Morno (31-60)'),
        ('quente', 'Lead Quente (61-80)'),
        ('muito_quente', 'Lead Muito Quente (81-100)')
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    interesse = forms.ChoiceField(
        choices=INTERESSE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    classificacao_score = forms.ChoiceField(
        choices=SCORE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Classificação de Score'
    )
    
    responsavel = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role__in=['vendedor', 'supervisor']),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todos os responsáveis"
    )
    
    data_criacao_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Criado a partir de'
    )
    
    data_criacao_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Criado até'
    )
    
    valor_interesse_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
        label='Valor mínimo de interesse'
    )
    
    sem_atividade_dias = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'placeholder': 'Ex: 7'
        }),
        label='Sem atividade há quantos dias?'
    )


class ExecutarWorkflowForm(forms.Form):
    """
    Formulário para executar workflow em leads selecionados.
    """
    workflow = forms.ModelChoiceField(
        queryset=Workflow.objects.filter(ativo=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    leads_selecionados = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['workflow'].empty_label = "Selecione um workflow"


class AdicionarCampanhaForm(forms.Form):
    """
    Formulário para adicionar leads a uma campanha.
    """
    campanha = forms.ModelChoiceField(
        queryset=CampanhaNutricao.objects.filter(status='ativa'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    leads_selecionados = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['campanha'].empty_label = "Selecione uma campanha"
