"""
Middleware para interceptar e tratar erros de URL (NoReverseMatch) automaticamente.

Este middleware captura exceções NoReverseMatch que ocorrem quando uma URL
não pode ser resolvida, e tenta encontrar uma URL compatível usando
o sistema de mapeamento de URLs.
"""

from django.urls import NoReverseMatch
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from roar_crm.url_mappings import get_url_name


class URLCompatibilityMiddleware(MiddlewareMixin):
    """
    Middleware que captura exceções NoReverseMatch e tenta
    encontrar URLs alternativas baseadas no mapeamento de URLs.
    """

    def process_exception(self, request, exception):
        """
        Processa exceções que ocorrem durante o processamento da requisição.
        Se for uma NoReverseMatch, tenta encontrar uma URL alternativa.

        Args:
            request: O objeto request do Django
            exception: A exceção que foi lançada

        Returns:
            HttpResponse: Uma resposta para redirecionar o usuário, ou None
        """
        # Se não for NoReverseMatch, deixa o Django processar normalmente
        if not isinstance(exception, NoReverseMatch):
            return None

        # Obter informações da exceção
        error_msg = str(exception)

        # Tentar extrair o nome da URL da mensagem de erro
        import re
        url_pattern = re.compile(r"['\"]([a-zA-Z0-9_:]+)['\"]")
        url_matches = url_pattern.findall(error_msg)

        if not url_matches:
            # Se não conseguir extrair a URL, só registrar o erro
            if settings.DEBUG:
                messages.error(
                    request,
                    f"Erro de URL: Não foi possível resolver uma URL. Detalhes: {error_msg}"
                )
            return None

        # Tentar encontrar uma URL compatível para cada URL extraída
        for old_url_name in url_matches:
            # Verificar se é uma URL com namespace
            if ':' in old_url_name:
                # Tentar encontrar uma URL compatível
                new_url_name = get_url_name(old_url_name)
                
                if new_url_name != old_url_name:
                    # Se encontrou, tentar redirecionar para a home
                    try:
                        from django.urls import reverse
                        new_url = reverse('home')
                        
                        if settings.DEBUG:
                            messages.warning(
                                request,
                                f"URL '{old_url_name}' não existe mais. "
                                f"Redirecionado para a home. "
                                f"Possível substituta: '{new_url_name}'."
                            )
                        
                        return HttpResponseRedirect(new_url)
                    except:
                        # Se ainda falhar, apenas registre o erro e retorne None
                        if settings.DEBUG:
                            messages.error(
                                request,
                                f"Erro de URL: Não foi possível resolver '{old_url_name}'. "
                                f"Tentou mapear para '{new_url_name}', mas também falhou."
                            )
        
        # Se não conseguir resolver, apenas registre o erro e retorne None
        if settings.DEBUG:
            messages.error(
                request,
                f"Erro de URL não resolvido: {error_msg}"
            )
        
        return None
