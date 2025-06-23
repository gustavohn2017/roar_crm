# Funil de Vendas - Lions CRM

## Visão Geral

A implementação do Funil de Vendas foi completamente reestruturada para garantir:

- **Modularidade**: Componentes reutilizáveis e independentes
- **Performance**: Otimizações para carregamento e renderização rápidos
- **Compatibilidade**: Suporte para diferentes navegadores e dispositivos
- **Manutenibilidade**: Código organizado e bem documentado

## Estrutura de Arquivos

```
templates/vendedores/utils/
├── funil_vendas.html
└── components/
    ├── funnel-visualization.html
    ├── kanban-column.html
    └── lead-card.html

static/
├── css/
│   └── sales-funnel.css
└── js/
    ├── stats-formatter.js
    ├── funnel-kanban.js
    ├── funnel-optimizer.js
    └── funnel-test.js

docs/ui/
├── SALES_FUNNEL_DOCUMENTATION.md
└── BROWSER_COMPATIBILITY_TESTS.md
```

## Principais Melhorias

1. **CSS Consolidado**
   - Arquivo único para todos os estilos do funil
   - Variáveis CSS para fácil personalização
   - Verificação de carregamento com fallbacks de emergência
   - Otimizações de performance (GPU, will-change, etc.)

2. **Componentes Modulares**
   - Visualização do funil separada em componente
   - Cards de leads padronizados e reutilizáveis
   - Colunas kanban flexíveis e parametrizáveis

3. **Otimizações de Performance**
   - Detecção de compatibilidade do navegador
   - Adaptações para dispositivos móveis
   - Lazy loading de recursos
   - Animações otimizadas com GPU

4. **Ferramentas de Teste**
   - Script de teste para verificação de componentes
   - Guia de teste para compatibilidade entre navegadores
   - Detecção automática de problemas de CSS

## Como Usar

### Template Principal

```html
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/sales-funnel.css' %}">
{% endblock %}

{% block content %}
<!-- ... conteúdo ... -->

<!-- Visualização do Funil -->
{% include 'vendedores/utils/components/funnel-visualization.html' %}

<!-- Kanban Board -->
<div class="kanban-board">
    <div class="board-scroller">
        <div class="board-container">
            {% include 'vendedores/utils/components/kanban-column.html' with 
                column_type="new" title="Novos" icon_class="bi-inbox-fill" leads=leads_novos %}
            
            <!-- Outras colunas... -->
        </div>
    </div>
</div>
{% endblock %}
```

### Componente de Coluna Kanban

```html
{% include 'vendedores/utils/components/kanban-column.html' with 
    column_type="new" 
    title="Novos" 
    icon_class="bi-inbox-fill" 
    leads=leads_novos %}
```

## Compatibilidade

Testado e otimizado para:
- Chrome 80+
- Firefox 75+
- Edge 80+
- Safari 13.1+
- Mobile: iOS Safari 13.4+, Android Chrome

## Documentação

Para informações detalhadas sobre a implementação, consulte:
- [Documentação Completa](docs/ui/SALES_FUNNEL_DOCUMENTATION.md)
- [Guia de Testes de Compatibilidade](docs/ui/BROWSER_COMPATIBILITY_TESTS.md)

## Manutenção

### Executando testes

Para administradores e staff, um script de teste está disponível:

```javascript
// No console do navegador
runFunnelTests();
```

### Atualizando os estilos

Após modificações no CSS ou JavaScript, execute:

```
python manage.py collectstatic --noinput
```

---

**Desenvolvido por:** Equipe Lions CRM  
**Versão:** 3.2  
**Data:** 13/06/2025
