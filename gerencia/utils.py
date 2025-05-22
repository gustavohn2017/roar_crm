import csv
from django.http import HttpResponse
from datetime import datetime

def export_to_csv(data, filename, headers):
    """
    Utilitário para exportar dados para CSV
    
    Args:
        data: Lista de dicionários com os dados a serem exportados
        filename: Nome do arquivo sem a extensão
        headers: Dicionário com chave=coluna no dicionário e valor=nome da coluna no CSV
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{timestamp}.csv"'
    
    writer = csv.writer(response)
    
    # Escrevendo cabeçalho
    writer.writerow(headers.values())
    
    # Escrevendo dados
    for item in data:
        row = [item.get(key, '') for key in headers.keys()]
        writer.writerow(row)
        
    return response
