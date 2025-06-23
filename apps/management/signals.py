"""
Signal handlers for the management application.

These signals help maintain consistency between User and Profile models.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update user profile when a user is saved.
    
    Args:
        sender: Model class sending signal
        instance: User instance that was saved
        created: Whether this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
