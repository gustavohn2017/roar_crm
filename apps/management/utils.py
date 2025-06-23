"""
Utility functions for management module.
Includes data export, report generation and other helper functions.
"""
import csv
from django.http import HttpResponse
from datetime import datetime
from typing import Dict, List, Any, Union


def export_to_csv(data: List[Dict[str, Any]], filename: str, headers: Dict[str, str]) -> HttpResponse:
    """
    Utility for exporting data to CSV
    
    Args:
        data: List of dictionaries containing data to be exported
        filename: Base filename without extension
        headers: Dictionary with key=column in dictionary and value=column name in CSV
        
    Returns:
        HttpResponse with CSV content attachment
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{timestamp}.csv"'
    
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow(headers.values())
    
    # Write data rows
    for item in data:
        row = [item.get(key, '') for key in headers.keys()]
        writer.writerow(row)
        
    return response


def format_percentage(value: Union[float, int], decimal_places: int = 1) -> str:
    """
    Format a number as percentage string
    
    Args:
        value: Number to format
        decimal_places: Number of decimal places to include
        
    Returns:
        Formatted percentage string with % symbol
    """
    return f"{round(float(value), decimal_places)}%"


def format_currency(value: Union[float, int], currency_symbol: str = 'R$') -> str:
    """
    Format a number as currency string
    
    Args:
        value: Number to format
        currency_symbol: Currency symbol to prepend
        
    Returns:
        Formatted currency string
    """
    return f"{currency_symbol} {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def calculate_percentage(numerator: Union[float, int], denominator: Union[float, int], 
                         default: Union[float, int] = 0) -> float:
    """
    Safely calculate percentage without division by zero
    
    Args:
        numerator: Value in numerator
        denominator: Value in denominator 
        default: Default value if denominator is zero
        
    Returns:
        Calculated percentage or default value
    """
    return (numerator / denominator * 100) if denominator > 0 else default
