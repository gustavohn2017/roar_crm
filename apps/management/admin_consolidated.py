"""
Admin interface configuration for the management app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    """Inline admin for user profiles."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    """Customized User admin with integrated profile."""
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'get_role', 'date_joined')
    list_filter = ('profile__role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def get_role(self, obj):
        """Get user's role from profile."""
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else '-'
    get_role.short_description = 'Função'
    get_role.admin_order_field = 'profile__role'
    
    def get_inline_instances(self, request, obj=None):
        """Customize inline instances for User admin."""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# Unregister the default User admin
admin.site.unregister(User)

# Register with our custom admin
admin.site.register(User, CustomUserAdmin)
