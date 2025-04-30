from django import forms
from .models import TentativaContato


class TentativaContatoForm(forms.ModelForm):
    class Meta:
        model = TentativaContato
        fields = ['resultado', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }