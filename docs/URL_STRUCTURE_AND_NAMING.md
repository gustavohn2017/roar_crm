# URL Structure and Naming Conventions

## Overview

This document outlines the URL structure and naming conventions used in the Roar CRM system. It's designed to help developers understand how URLs are organized and how to maintain consistency when adding new routes.

## Namespace Structure

The application uses Django's URL namespaces to organize routes across different apps:

| Namespace | App | Purpose |
|-----------|-----|---------|
| `main` | vendedores | Main dashboard and vendor functionality |  
| `leads` | leads | Lead management |
| `gerencia` | gerencia | Administration and management |
| `automacao` | automacao | Marketing automation |

## Key URL Patterns

### Main Dashboard (vendedores app)

```python
# Namespace: main
path('', views.dashboard_vendedor, name='dashboard_principal'),
path('dashboard/', views.dashboard_vendedor, name='dashboard_principal_alt'),
path('dashboard/', views.dashboard_vendedor, name='dashboard'),  # Alias for compatibility
```

> **Note**: Both `main:dashboard` and `main:dashboard_principal` refer to the same view for backward compatibility.

### Lead Management (leads app)

```python
# Namespace: leads
path('list/', views.lead_list, name='list'),
path('create/', views.lead_create, name='create'),
path('quick-create/', views.lead_create_quick, name='create_quick'),
path('<int:lead_id>/', views.lead_detail, name='detail'),
```

## URL Compatibility Layer

To maintain backward compatibility during the refactoring process, we've created URL compatibility layers in each app. These layers map old URL patterns to new ones, which helps prevent breaking existing code that may reference the old URLs.

### Compatibility Files

Each app now has a dedicated compatibility file:

- `leads/urls_compatibility.py`
- `vendedores/urls_compatibility.py` 
- `gerencia/urls_compatibility.py`
- `automacao/urls_compatibility.py`

### Examples of URL Mapping

**Leads App:**
```python
# Old URL: /leads/lista/
# New URL: /leads/list/
path('lista/', redirect_lista_leads, name='lista_leads'),
```

**Vendedores App:**
```python
# Old URL: /main/home/
# New URL: /main/dashboard/
path('home/', redirect_to_dashboard, name='home'),
```

**Gerencia App:**
```python
# Old URL: /gerencia/painel-controle/
# New URL: /gerencia/painel/
path('painel-controle/', redirect_to_dashboard, name='painel_controle'),
```

**Automacao App:**
```python
# Old URL: /automacao/workflow/
# New URL: /automacao/workflows/
path('workflow/', redirect_to_workflows, name='workflow'),
```

## Common Issues and Fixes

### NoReverseMatch Errors

If you encounter a "NoReverseMatch" error:

1. Check that you're using the correct namespace (e.g., `main:dashboard` not just `dashboard`)
2. Verify the URL name exists in the corresponding app's urls.py file
3. Make sure you're passing all required parameters for the URL pattern
4. Check if you need to use one of the compatibility URL names instead

### Standard URL Patterns Across Apps

For consistency, we've implemented standard URL names across all app namespaces:

| URL Name | Purpose | Available in |
|----------|---------|-------------|
| `index` | Default landing page for the app | All apps |
| `dashboard` | Dashboard view for the app | All apps |
| `list` | List view for main model | Most apps |
| `create` | Create view for main model | Most apps |
| `detail` | Detail view for main model | Most apps |
| `update` | Update view for main model | Most apps |
| `delete` | Delete view for main model | Most apps |

## Standard Dashboard URLs

Each app now has a standard `dashboard` URL pattern to ensure consistency:

- `main:dashboard` - Main vendor dashboard
- `leads:dashboard` - Leads overview dashboard (redirects to list)
- `gerencia:dashboard` - Administrative dashboard
- `automacao:dashboard` - Automation dashboard

## Centralized URL Compatibility

To make URL compatibility management easier, we've implemented a comprehensive system:

1. Individual compatibility files per app (`urls_compatibility.py`)
2. Standardized redirection patterns for common URL patterns
3. URL tests to verify proper routing and detect broken URL references
4. A centralized URL mapping system in `roar_crm/url_mappings.py`
5. Context processors for template-level URL compatibility
6. Custom template tags for handling compatibility in templates

### URL Compatibility System Components:

#### 1. URL Mappings Module

The `roar_crm/url_mappings.py` module provides centralized mappings for:
- Old namespace to new namespace mappings (e.g., 'vendedores' → 'main')
- Specific URL name mappings (e.g., 'vendedores:dashboard' → 'main:dashboard')
- Renamed URLs within the same namespace

```python
# Example usage in Python code:
from roar_crm.url_mappings import get_url_name

# Will return 'main:dashboard'
new_url = get_url_name('vendedores:dashboard')
```

#### 2. Context Processors

The `roar_crm/context_processors.py` module adds URL compatibility helpers to all templates:

```django
{# Example usage in templates: #}
<a href="{{ get_compatible_url 'vendedores:dashboard' }}">Dashboard</a>

{% if url_exists 'vendedores:eventos_list' %}
    <a href="{{ get_compatible_url 'vendedores:eventos_list' }}">Eventos</a>
{% endif %}
```

#### 3. Template Tags

Custom template tags in `roar_crm/templatetags/url_compat.py` provide advanced URL compatibility:

```django
{% load url_compat %}

{# Generate compatible URL #}
<a href="{% compat_url 'vendedores:dashboard' %}">Dashboard</a>

{# Check if URL exists #}
{% if 'vendedores:eventos_list'|url_exists %}
    <a href="{% compat_url 'vendedores:eventos_list' %}">Eventos</a>
{% endif %}

{# Show URL mapping for debugging #}
Original: vendedores:dashboard, Mapped to: {% map_url 'vendedores:dashboard' %}
```

## URL Testing

The system now includes automated tests for URL routing in `roar_crm/tests/test_url_routing.py`. These tests verify:

1. That all primary URLs exist and don't raise `NoReverseMatch` errors
2. That all compatibility URLs properly redirect to their new counterparts
3. That the home redirect works correctly for all user types

## Best Practices for URL Management

When adding new URLs:

1. Always use the app's namespace when referring to URLs (`main:dashboard`, not just `dashboard`)
2. Follow the standard naming conventions outlined in this document
3. If replacing an existing URL pattern, add compatibility redirects
4. Add tests for any new URL patterns
5. Keep all URLs for a specific feature grouped in the URLs file
6. Use descriptive names that indicate the purpose of the view

## URL Naming Best Practices

1. Use clear, descriptive names that indicate the view's purpose
2. Use underscores to separate words in URL names (e.g., `lead_detail`)
3. Use singular nouns for detail views and plural for list views
4. Consistency is more important than brevity
| `dashboard` | Dashboard/overview for the app | All apps |
| `list` | List view of main resources | Most apps |
| `create` | Creation form for resources | Most apps |
| `detail` | Detail view for a specific resource | Most apps |

### Common URL Patterns by App

**Main (vendedores):**
- `main:dashboard` - Main dashboard
- `main:dashboard_principal` - Same as above (alias)
- `main:historico_contatos` - Contact history
- `main:detalhes_lead` - Lead details

**Leads:**
- `leads:list` - List all leads
- `leads:create` - Create new lead
- `leads:detail` - View lead details
- `leads:template_list` - List communication templates

**Gerencia:**
- `gerencia:dashboard` - Admin dashboard
- `gerencia:painel_admin` - Same as above (alias)
- `gerencia:vendedores` - Vendors management
- `gerencia:funcionarios` - Employee management

**Automacao:**
- `automacao:dashboard` - Automation dashboard
- `automacao:workflow_list` - List workflows
- `automacao:campanha_list` - List campaigns
- `automacao:lead_scoring_list` - Lead scoring tools

### Adding New URLs

When adding new URL patterns:

1. Follow the established naming conventions for the app
2. Update this documentation
3. Consider adding compatibility redirects for any URLs that might be referenced elsewhere

## Root URL Handling

The root URL (`/`) redirects to `main:dashboard` in the `home_redirect` view defined in `roar_crm/views.py`.

---

*Last updated: June 10, 2025*
