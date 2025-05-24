# API para o dashboard
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Lead
import logging

logger = logging.getLogger(__name__)

@login_required
def leads_api_list(request):
    """API simples para fornecer lista de leads para o dashboard."""
    try:
        # Buscar todos os leads com base nos parâmetros da query
        leads = Lead.objects.all().order_by('-data_criacao')
        
        # Aplicar filtros se existirem na query
        status = request.GET.get('status')
        interesse = request.GET.get('interesse')
        
        if status:
            leads = leads.filter(status=status)
        if interesse:
            leads = leads.filter(interesse=interesse)
        
        # Limitar resultados para performance
        leads = leads[:100]  # Limita a 100 leads para não sobrecarregar
        
        # Converter para o formato de resposta
        result = []
        for lead in leads:
            try:
                lead_data = {
                    'id': lead.id,
                    'nome': lead.nome,
                    'telefone': lead.telefone or 'N/A',
                    'email': lead.email or 'N/A',
                    'status': lead.status,
                    'status_display': lead.get_status_display(),
                    'interesse': lead.interesse,
                    'interesse_display': lead.get_interesse_display() if lead.interesse else 'N/A',
                    'data_criacao': lead.data_criacao.isoformat() if lead.data_criacao else None,
                    'data_ultimo_contato': lead.data_ultimo_contato.isoformat() if lead.data_ultimo_contato else None,
                }
                
                # Adicionar valor potencial apenas se existir
                if hasattr(lead, 'valor_potencial') and lead.valor_potencial is not None:
                    try:
                        lead_data['valor_potencial'] = float(lead.valor_potencial)
                    except (TypeError, ValueError):
                        lead_data['valor_potencial'] = 0
                else:
                    lead_data['valor_potencial'] = 0
                
                result.append(lead_data)
            except Exception as lead_error:
                logger.error(f"Erro ao processar lead {lead.id}: {str(lead_error)}")
                # Continuar para o próximo lead em caso de erro
                continue
        
        return JsonResponse(result, safe=False)
    except Exception as e:
        logger.error(f"Erro na API de leads: {str(e)}")
        return JsonResponse({"error": "Ocorreu um erro ao buscar os leads"}, status=500)
