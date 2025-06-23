from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    """
    Template filter that checks if a user has a specific role or higher.
    Usage: {% if user|has_role:"gerente" %}
    """
    if not hasattr(user, 'profile'):
        return False
    
    if hasattr(user.profile, 'has_role_or_higher'):
        return user.profile.has_role_or_higher(role_name)
    
    # Fallback if method doesn't exist
    return user.is_staff or user.is_superuser
