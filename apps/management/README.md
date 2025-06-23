# Management App Reorganization

## Structure Overview

The `gerencia` app has been reorganized into `apps/management` with the following consolidated files:

```
apps/
  management/
    __init__.py            - Default app configuration
    admin_consolidated.py  - Enhanced admin interface with Profile integration
    apps.py                - App configuration
    decorators.py          - Access control decorators (admin_required, etc.)
    forms_consolidated.py  - User & profile forms
    models.py              - Profile model with role hierarchy
    signals.py             - Signal handlers for User-Profile sync
    urls_consolidated.py   - URL routing for management features
    utils.py               - Helper functions (CSV export, formatting)
    views_consolidated.py  - View functions for all management features
```

## Key Improvements

1. **Role-based Access Control**:
   - Clear hierarchy (admin > supervisor > vendedor)
   - Consistent permission checks with decorators

2. **User Management**:
   - Complete user lifecycle (create, read, update, delete)
   - Enhanced profile with additional metadata
   - Password management

3. **Performance Reporting**:
   - Comprehensive dashboards for management
   - Team performance metrics
   - Individual employee analytics
   - Historical data tracking

4. **Data Export**:
   - Export users, contacts, and leads to CSV
   - Customizable exports with filtering

5. **Code Quality**:
   - Type hints throughout the codebase
   - Comprehensive docstrings
   - Optimized database queries
   - Consistent styling and naming

## Migration Notes

- The templates need to be updated from `gerencia/` to `management/`
- Update URL references from `gerencia:` to `management:`
- Update import paths in other apps from `gerencia.decorators` to `apps.management.decorators`

## Next Steps

- Update main `urls.py` to use the new consolidated URLs
- Move and update templates to match the new structure
- Update settings to include the new app path
