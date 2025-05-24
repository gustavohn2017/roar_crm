from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtém um item de um dicionário usando a chave."""
    if dictionary is None:
        return None
    try:
        return dictionary[key]
    except (KeyError, TypeError):
        return None
