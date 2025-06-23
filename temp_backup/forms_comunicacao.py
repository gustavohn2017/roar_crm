from django import forms
from .models_comunicacao import TemplateWhatsApp, TemplateEmail, HistoricoContato


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
            'rows': 4, 
            'placeholder': 'Digite sua mensagem para o WhatsApp...',
            'id': 'mensagem-whatsapp'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('mensagem'):
            if not cleaned_data.get('template'):
                raise forms.ValidationError("Você deve escolher um template ou digitar uma mensagem.")
        return cleaned_data


class EnviarEmailForm(forms.Form):
    """Formulário para enviar e-mails."""
    template = forms.ModelChoiceField(
        queryset=TemplateEmail.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select mb-2', 'id': 'template-email'})
    )
    
    assunto = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2',
            'placeholder': 'Assunto do e-mail',
            'id': 'assunto-email'
        })
    )
    
    corpo = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control wysiwyg-editor',
            'rows': 10,
            'placeholder': 'Conteúdo do e-mail...',
            'id': 'corpo-email'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('assunto'):
            raise forms.ValidationError("O assunto do e-mail é obrigatório.")
        if not cleaned_data.get('corpo'):
            if not cleaned_data.get('template'):
                raise forms.ValidationError("Você deve escolher um template ou digitar o conteúdo do e-mail.")
        return cleaned_data


class RegistrarContatoForm(forms.ModelForm):
    """Formulário para registrar contatos manuais."""
    class Meta:
        model = HistoricoContato
        fields = ['tipo', 'conteudo', 'foi_respondido', 'data_resposta']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foi_respondido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_resposta': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
        }
