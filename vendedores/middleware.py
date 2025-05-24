from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve


class RestricaoHistoricoMiddleware:
    """
    Middleware para restringir o acesso de vendedores ao histórico de contatos
    e ao painel administrativo do Django
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.user.is_authenticated:
            # Verifica se o usuário tem perfil (para evitar erros com usuários antigos)
            hasattr_profile = hasattr(request.user, "profile")
            
            # Somente aplica restrições para usuários que não são admins nem supervisores
            if hasattr_profile and not request.user.profile.has_role_or_higher('supervisor'):
                try:
                    current_url = resolve(request.path_info)
                    
                    # Impedir acesso � view de hist�rico de contatos
                    if current_url.url_name == "historico_contatos":
                        messages.warning(request, "Acesso ao hist�rico de contatos restrito.")
                        return redirect("vendedores:dashboard_vendedor")
                except:
                    pass
                    
                # Impedir acesso ao painel administrativo do Django (desativado)
                if request.path.startswith("/admin/"):
                    messages.warning(request, "O painel administrativo do Django está desativado. Por favor, use as ferramentas do CRM.")
                    return redirect("vendedores:dashboard_vendedor")

        response = self.get_response(request)
        
        # Remover botão/link para o painel administrativo se o usuário não for staff e nem supervisor
        if request.user.is_authenticated:
            hasattr_profile = hasattr(request.user, "profile")
            
            # Verifica se o usuário não tem permissão para acessar o painel de admin
            if hasattr_profile and not request.user.profile.has_role_or_higher('supervisor'):
                if "text/html" in response.get("Content-Type", ""):
                    if hasattr(response, "content"):
                        # Converte para string se for bytes
                        content = response.content.decode("utf-8") if isinstance(response.content, bytes) else response.content
                        
                        # Remove links para o admin nas páginas HTML (não necessário após remover totalmente o admin)
                        pass
                        
                        # Converte de volta para bytes se necessário
                        if isinstance(response.content, bytes):
                            response.content = content.encode("utf-8")
                        else:
                            response.content = content
                    
        return response
