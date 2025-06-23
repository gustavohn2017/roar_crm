"""
Central URL compatibility management module for Roar CRM.

This module provides utilities for creating and managing URL compatibility
redirects across all apps in the system. It allows for easier maintenance
and consistent handling of URL redirections.
"""

from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch


class CompatibilityRouter:
    """
    A utility class for creating URL compatibility routes.
    This class makes it easier to create standardized URL redirects.
    """
    
    def __init__(self, app_namespace):
        """
        Initialize the router with the app's namespace.
        
        Args:
            app_namespace (str): The namespace of the app (e.g., 'main', 'leads')
        """
        self.app_namespace = app_namespace
        self.mappings = []
    
    def add_redirect(self, old_path, new_name, **kwargs):
        """
        Add a redirect mapping from an old path to a new URL name.
        
        Args:
            old_path (str): The old URL path pattern
            new_name (str): The new URL name to redirect to
            **kwargs: Any arguments required by the URL
        """
        def redirect_view(request):
            try:
                target_url = reverse(f"{self.app_namespace}:{new_name}", kwargs=kwargs)
                return redirect(target_url)
            except NoReverseMatch:
                # Fallback to the homepage if the URL can't be found
                return redirect('home')
        
        # Create a descriptive name for the redirect view
        old_name = f"old_{old_path.replace('/', '_').strip('_')}"
        if not old_name:
            old_name = f"old_index_{new_name}"
        
        # Store the mapping for later use
        self.mappings.append((old_path, old_name, redirect_view))
        
        return self
    
    def get_urlpatterns(self):
        """
        Get the Django URL patterns for all the added redirects.
        
        Returns:
            list: A list of URL patterns
        """
        urlpatterns = []
        
        for old_path, old_name, view_func in self.mappings:
            urlpatterns.append(path(old_path, view_func, name=old_name))
        
        return urlpatterns


# Example usage:
"""
from roar_crm.url_compatibility import CompatibilityRouter

# In your urls_compatibility.py file:
router = CompatibilityRouter('leads')

# Add redirects
router.add_redirect('lista/', 'list')
router.add_redirect('cadastrar/', 'create')
router.add_redirect('<int:lead_id>/', 'detail', lead_id=0)  # The lead_id will be replaced dynamically

# Get the URL patterns
urlpatterns = router.get_urlpatterns()
"""

def check_url_exists(url_name):
    """
    Check if a URL exists in the system.
    
    Args:
        url_name (str): The full URL name including namespace (e.g., 'main:dashboard')
    
    Returns:
        bool: True if the URL exists, False otherwise
    """
    try:
        reverse(url_name)
        return True
    except NoReverseMatch:
        return False


def get_compatible_url(primary_url, fallback_url=None):
    """
    Get a URL that exists in the system, with a fallback.
    Useful when different versions of the system might have different URL names.
    
    Args:
        primary_url (str): The primary URL name to try
        fallback_url (str, optional): The fallback URL name if primary doesn't exist
        
    Returns:
        str: The URL name that exists in the system
    
    Raises:
        NoReverseMatch: If neither the primary nor fallback URL exists
    """
    if check_url_exists(primary_url):
        return primary_url
        
    if fallback_url and check_url_exists(fallback_url):
        return fallback_url
        
    # If neither exists, raise an exception with both names
    raise NoReverseMatch(f"Neither URL '{primary_url}' nor '{fallback_url}' exist in the system.")
