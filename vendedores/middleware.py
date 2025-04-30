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
        if request.user.is_authenticated and not request.user.is_staff:
            current_url = resolve(request.path_info)
            
            # Impedir acesso à view de histórico de contatos
            if current_url.url_name == 'historico_contatos':
                messages.warning(request, 'Acesso ao histórico de contatos restrito.')
                return redirect('dashboard_vendedor')
                
            # Impedir acesso ao painel administrativo do Django
            if request.path.startswith('/admin/'):
                messages.warning(request, 'Acesso restrito. Você não tem permissão para acessar o painel administrativo.')
                return redirect('dashboard_vendedor')

        response = self.get_response(request)
        
        # Remover botão/link para o painel administrativo se o usuário não for staff
        if request.user.is_authenticated and not request.user.is_staff and 'text/html' in response.get('Content-Type', ''):
            if hasattr(response, 'content'):
                # Converte para string se for bytes
                content = response.content.decode('utf-8') if isinstance(response.content, bytes) else response.content
                
                # Remove links para o admin nas páginas HTML
                content = content.replace('<a href="/admin/"', '<a style="display:none" href="#"')
                content = content.replace('<a href="/admin"', '<a style="display:none" href="#"')
                
                # Converte de volta para bytes se necessário
                if isinstance(response.content, bytes):
                    response.content = content.encode('utf-8')
                else:
                    response.content = content
                    
        return response