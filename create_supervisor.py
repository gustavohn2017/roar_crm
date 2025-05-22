"""
Script para criar um usuário supervisor para testes
"""
from django.contrib.auth.models import User
from gerencia.models import Profile

try:
    supervisor = User.objects.get(username='supervisor')
    print('Usuário supervisor já existe')
    
    # Update role if needed
    profile = supervisor.profile
    if profile.role != 'supervisor':
        profile.role = 'supervisor'
        profile.save()
        print('Perfil atualizado para supervisor')
    
except User.DoesNotExist:
    # Create supervisor user
    supervisor = User.objects.create_user(
        username='supervisor',
        email='supervisor@example.com',
        password='senha123',
        first_name='Super',
        last_name='Visor',
        is_staff=False
    )
    
    # Set profile as supervisor
    profile = supervisor.profile
    profile.role = 'supervisor'
    profile.save()
    
    print('Usuário supervisor criado com sucesso')
    
print(f'Username: supervisor')
print(f'Senha: senha123')
print(f'Função: {profile.get_role_display()}')
