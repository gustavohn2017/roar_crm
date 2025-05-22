from django import forms
from django.contrib.auth.models import User
from .models import Profile

class FuncionarioForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a senha', widget=forms.PasswordInput)
    role = forms.ChoiceField(label='Função', choices=Profile.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', 'As senhas não coincidem.')
        return cleaned_data
        
    def save(self, commit=True):
        # Salva o usuário primeiro
        user = super().save(commit=False)
        
        # Se for admin, marca is_staff como True
        if self.cleaned_data.get('role') == 'admin':
            user.is_staff = True
        else:
            user.is_staff = False
            
        if commit:
            user.save()
            # Atualiza o perfil após salvar o usuário
            profile = user.profile
            profile.role = self.cleaned_data.get('role')
            profile.save()
            
        return user
