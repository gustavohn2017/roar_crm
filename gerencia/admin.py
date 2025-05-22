"""
Configuração do painel administrativo do Django para os modelos do app gerencia.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = UserAdmin.list_filter + ('profile__role',)
    
    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Função'
    get_role.admin_order_field = 'profile__role'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# Re-registrar o modelo User com o novo admin personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
