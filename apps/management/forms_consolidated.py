"""
Forms for user management, profiles, and related functionality.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class FuncionarioForm(forms.ModelForm):
    """
    Form for creating and editing employees (users with profiles).
    Handles user data and profile roles in a single form.
    """
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'})
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme a senha'})
    )
    role = forms.ChoiceField(
        label='Função',
        choices=Profile.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    phone = forms.CharField(
        label='Telefone',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'})
    )
    bio = forms.CharField(
        label='Biografia',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Breve descrição do funcionário',
            'rows': 3
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }

    def clean(self):
        """Validate that passwords match and other validations."""
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', 'As senhas não coincidem.')
        return cleaned_data
        
    def save(self, commit=True):
        """Save user and related profile with role information."""
        # Save user first
        user = super().save(commit=False)
        
        # Set password
        user.set_password(self.cleaned_data.get('password1'))
        
        if commit:
            user.save()
            # Update profile after saving user
            profile = user.profile
            profile.role = self.cleaned_data.get('role')
            profile.phone = self.cleaned_data.get('phone')
            profile.bio = self.cleaned_data.get('bio')
            profile.save()
            
        return user


class FuncionarioEditForm(forms.ModelForm):
    """
    Form for editing existing employees without changing password.
    """
    role = forms.ChoiceField(
        label='Função',
        choices=Profile.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    phone = forms.CharField(
        label='Telefone',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'})
    )
    bio = forms.CharField(
        label='Biografia',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Breve descrição do funcionário',
            'rows': 3
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        """Initialize form with user profile data."""
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['role'].initial = self.instance.profile.role
            self.fields['phone'].initial = self.instance.profile.phone
            self.fields['bio'].initial = self.instance.profile.bio
            
    def save(self, commit=True):
        """Save user and update profile data."""
        user = super().save(commit=False)
        
        if commit:
            user.save()
            # Update profile
            profile = user.profile
            profile.role = self.cleaned_data.get('role')
            profile.phone = self.cleaned_data.get('phone')
            profile.bio = self.cleaned_data.get('bio')
            profile.save()
            
        return user


class StyledLoginForm(AuthenticationForm):
    """
    Enhanced login form with Bootstrap styling.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome de usuário',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        })
    )


class PasswordChangeForm(forms.Form):
    """
    Form for changing a user's password.
    """
    current_password = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        """Validate that new passwords match."""
        cleaned_data = super().clean()
        if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            self.add_error('new_password2', 'As senhas não coincidem.')
        return cleaned_data
