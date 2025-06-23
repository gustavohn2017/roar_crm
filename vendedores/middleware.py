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
                    
                    # Impedir acesso à view de histórico de contatos
                    if current_url.url_name == "historico_contatos":
                        messages.warning(request, "Acesso ao histórico de contatos restrito.")
                        return redirect("vendedores:dashboard_vendedor")
                except:
                    pass
                    
                # Impedir acesso ao painel administrativo do Django (desativado)
                if request.path.startswith("/admin/"):
                    messages.warning(request, "O painel administrativo do Django está desativado. Por favor, use as ferramentas do CRM.")
                    return redirect("vendedores:dashboard_vendedor")

        response = self.get_response(request)
        
        # O código abaixo foi otimizado para remover processamento desnecessário
        # Uma vez que o painel admin foi desativado, não precisamos modificar o HTML de resposta
                    
        return response
