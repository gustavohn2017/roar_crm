from .models import Lead

def lead_choices(request):
    """
    Adiciona as choices do modelo Lead ao contexto global de templates.
    Permite acessar em qualquer template, especialmente útil para o modal de cadastro rápido.
    """
    return {
        'interesse_choices': Lead.INTEREST_CHOICES,
        'fonte_choices': Lead.SOURCE_CHOICES,
        'status_choices': Lead.STATUS_CHOICES,
    }
