"""
Models for user profiles and management-related entities.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Dict, List, Tuple, Literal, Optional, Union, Any, TypedDict, ClassVar


class Profile(models.Model):
    """
    Extended profile for system users.
    Includes additional data beyond the standard Django User model.
    
    Attributes:
        user: Django User this profile is associated with
        role: User's role in the system (admin, supervisor, vendedor)
        phone: User's phone number
        bio: User's biography or description
        date_updated: Date of last profile update
    """
    ROLE_CHOICES: ClassVar[List[Tuple[str, str]]] = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('vendedor', 'Vendedor'),
    ]
    
    # Define role hierarchy (from highest to lowest permission level)
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
        """Check if user is administrator."""
        return self.role == 'admin'
    
    def is_supervisor(self) -> bool:
        """Check if user is supervisor."""
        return self.role == 'supervisor'
    
    def is_vendedor(self) -> bool:
        """Check if user is sales representative."""
        return self.role == 'vendedor'
    
    def has_role_or_higher(self, required_role: str) -> bool:
        """
        Check if user has the specified role or higher in the hierarchy.
        
        Args:
            required_role: The minimum required role ('admin', 'supervisor', 'vendedor')
            
        Returns:
            True if user has the required role or higher, False otherwise.
        """
        user_level = self.ROLE_HIERARCHY.get(self.role, 0)
        required_level = self.ROLE_HIERARCHY.get(required_role, 0)
        
        return user_level >= required_level
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
        indexes = [
            models.Index(fields=['role'], name='profile_role_idx'),
            models.Index(fields=['user'], name='profile_user_idx'),
        ]


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs) -> None:
    """
    Automatically create or update user profile when a user is created or modified.
    
    Args:
        sender: Model that sent the signal (User)
        instance: Model instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional arguments
    """
    if created:
        # Create default profile with vendedor role
        Profile.objects.create(user=instance)
    else:
        # Ensure profile exists
        Profile.objects.get_or_create(user=instance)