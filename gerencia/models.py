"""
Modelos para o perfil de usuário e outras entidades relacionadas à gestão de usuários.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Dict, List, Tuple, Literal, Optional, Union, Any, TypedDict, ClassVar


class Profile(models.Model):
    """
    Perfil estendido para os usuários do sistema.
    Inclui dados adicionais aos do model User padrão do Django.
    
    Atributos:
        user: Usuário do Django ao qual este perfil está associado
        role: Papel/função do usuário no sistema (admin, supervisor, vendedor)
        phone: Número de telefone do usuário
        bio: Biografia ou descrição do usuário
        date_updated: Data da última atualização do perfil
    """
    ROLE_CHOICES: ClassVar[List[Tuple[str, str]]] = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('vendedor', 'Vendedor'),
    ]
    
    # Definir a hierarquia de papéis (do maior para o menor nível de permissão)
    ROLE_HIERARCHY: ClassVar[Dict[str, int]] = {
        'admin': 3,
        'supervisor': 2,
        'vendedor': 1
    }
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField("Função", max_length=20, choices=ROLE_CHOICES, default='vendedor')
    phone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    bio = models.TextField("Biografia", blank=True, null=True)
    date_updated = models.DateTimeField("Última atualização", auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador."""
        return self.role == 'admin'
    
    def is_supervisor(self) -> bool:
        """Verifica se o usuário é supervisor."""
        return self.role == 'supervisor'
        
    def is_vendedor(self) -> bool:
        """Verifica se o usuário é vendedor."""
        return self.role == 'vendedor'
    
    def has_role_or_higher(self, required_role: str) -> bool:
        """
        Verifica se o usuário tem o papel especificado ou superior na hierarquia.
        
        Args:
            required_role: O papel mínimo necessário ('admin', 'supervisor', 'vendedor')
            
        Returns:
            True se o usuário tem o papel requerido ou superior, False caso contrário.
        """
        user_level = self.ROLE_HIERARCHY.get(self.role, 0)
        required_level = self.ROLE_HIERARCHY.get(required_role, 0)
        
        return user_level >= required_level
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs) -> None:
    """
    Cria ou atualiza o perfil do usuário automaticamente quando um usuário é criado ou alterado.
    
    Args:
        sender: Modelo que enviou o sinal (User)
        instance: Instância do modelo que foi salva
        created: Booleano indicando se esta é uma nova instância
        **kwargs: Argumentos adicionais
    """
    if created:
        # Cria um perfil padrão com papel de vendedor
        Profile.objects.create(user=instance)
    else:
        # Garante que o perfil existe
        Profile.objects.get_or_create(user=instance)
