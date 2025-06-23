"""
Utilitários comuns para todas as aplicações do ROAR CRM.
"""

import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def export_to_csv(queryset, filename, fields_mapping):
    """
    Exporta um queryset Django para CSV.
    
    Args:
        queryset: QuerySet do Django
        filename: Nome do arquivo CSV
        fields_mapping: Dicionário {campo_model: nome_coluna_csv}
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('\ufeff')  # BOM para UTF-8
    
    writer = csv.writer(response)
    
    # Escrever cabeçalho
    writer.writerow(list(fields_mapping.values()))
    
    # Escrever dados
    for obj in queryset:
        row = []
        for field in fields_mapping.keys():
            value = obj
            for attr in field.split('__'):
                value = getattr(value, attr, '')
                if value is None:
                    value = ''
            
            if isinstance(value, datetime):
                value = value.strftime('%d/%m/%Y %H:%M')
            
            row.append(str(value))
        
        writer.writerow(row)
    
    return response


def format_phone(phone):
    """Formata número de telefone brasileiro."""
    if not phone:
        return ''
    
    # Remove tudo que não é número
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 11:  # Celular com DDD
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    elif len(digits) == 10:  # Fixo com DDD
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    
    return phone


def calculate_business_days_between(start_date, end_date):
    """Calcula dias úteis entre duas datas."""
    if not start_date or not end_date:
        return 0
    
    current = start_date
    business_days = 0
    
    while current <= end_date:
        if current.weekday() < 5:  # Segunda a sexta
            business_days += 1
        current += timedelta(days=1)
    
    return business_days


def get_month_range(date=None):
    """Retorna primeiro e último dia do mês."""
    if date is None:
        date = timezone.now().date()
    
    first_day = date.replace(day=1)
    
    if date.month == 12:
        last_day = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
    
    return first_day, last_day


def safe_divide(numerator, denominator, default=0):
    """Divisão segura que retorna um valor padrão se denominador for zero."""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


class DateTimeHelper:
    """Helper para operações com data e hora."""
    
    @staticmethod
    def get_week_start_end(date=None):
        """Retorna início e fim da semana."""
        if date is None:
            date = timezone.now().date()
        
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)
        return start, end
    
    @staticmethod
    def get_quarter_start_end(date=None):
        """Retorna início e fim do trimestre."""
        if date is None:
            date = timezone.now().date()
        
        quarter = (date.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        
        start = date.replace(month=start_month, day=1)
        
        if quarter == 4:
            end = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = date.replace(month=start_month + 3, day=1) - timedelta(days=1)
        
        return start, end
