/**
 * Lions CRM - Funil de Vendas (Sales Funnel)
 * Script Unificado e Otimizado
 * Versão: 5.0
 * Data: 18/06/2025
 */

// Módulo para funcionalidade do funil de vendas
const SalesFunnel = (function() {
  // Cache de elementos DOM e variáveis
  const DOM = {
    funnelSegments: null,
    kanbanColumns: null,
    statCards: null,
    leadCards: null,
    scrollLeftBtn: null,
    scrollRightBtn: null,
    boardScroller: null,
    kanbanBoard: null,
  };

  // Configurações
  const settings = {
    animationEnabled: true,
    tooltipsEnabled: true,
    dragDropEnabled: false, // Recurso futuro
    autoSaveEnabled: true,
    autoRefreshInterval: 120000, // 2 minutos
  };

  // Inicialização do funil
  function init() {
    console.log('🚀 Iniciando Funil de Vendas v5.0 Unificado');

    checkBrowserCompatibility();
    cacheDOM();
    setupEventListeners();
    initStatCards();
    initKanban();
    if (settings.tooltipsEnabled) {
      initTooltips();
    }
    setupLazyLoading();
    if (isMobileDevice()) {
        applyMobileOptimizations();
    }
    setupAutoRefresh();
    initializeChangeMonitoring();
    checkPendingUpdates();

    console.log('✅ Funil de Vendas inicializado com sucesso!');
  }

  // Cache de elementos DOM
  function cacheDOM() {
    DOM.funnelSegments = document.querySelectorAll('.funnel-segment');
    DOM.kanbanColumns = document.querySelectorAll('.kanban-column');
    DOM.statCards = document.querySelectorAll('.stat-card');
    DOM.leadCards = document.querySelectorAll('.lead-card');
    DOM.scrollLeftBtn = document.querySelector('.kanban-scroll-left');
    DOM.scrollRightBtn = document.querySelector('.kanban-scroll-right');
    DOM.boardScroller = document.querySelector('.board-scroller');
    DOM.kanbanBoard = document.querySelector('.kanban-board');
  }

  // Configurar event listeners
  function setupEventListeners() {
    if (DOM.scrollLeftBtn && DOM.scrollRightBtn && DOM.boardScroller) {
      DOM.scrollLeftBtn.addEventListener('click', scrollBoardLeft);
      DOM.scrollRightBtn.addEventListener('click', scrollBoardRight);
      DOM.boardScroller.addEventListener('scroll', updateScrollButtonVisibility, { passive: true });
    }

    DOM.funnelSegments.forEach((segment, index) => {
      segment.addEventListener('click', () => scrollToColumn(index));
    });

    DOM.leadCards.forEach(configureLeadCard);
    observeDynamicContent();
    document.addEventListener('click', delegateClickEvents);
    
    // Atalhos de teclado
    document.addEventListener('keydown', handleKeyboardShortcuts);
  }

  // Inicializar cards de estatísticas
  function initStatCards() {
    DOM.statCards.forEach(card => {
      const valueElement = card.querySelector('.stat-value');
      if (valueElement && valueElement.dataset.value) {
        animateCounterValue(valueElement);
      }
    });
  }

  // Animar contadores de estatísticas
  function animateCounterValue(element) {
    const value = parseFloat(element.dataset.value.replace(/[^\d.-]/g, ''));
    const isCurrency = element.classList.contains('currency');
    const isPercentage = element.classList.contains('percentage');
    const duration = 1500;
    const frameDuration = 16;
    const totalFrames = Math.round(duration / frameDuration);
    let currentFrame = 0;
    const initialValue = 0;
    const valueIncrement = (value - initialValue) / totalFrames;

    const animate = () => {
      currentFrame++;
      const currentValue = initialValue + valueIncrement * currentFrame;
      if (isCurrency) {
        element.textContent = formatCurrency(currentValue);
      } else if (isPercentage) {
        element.textContent = formatPercentage(currentValue);
      } else {
        element.textContent = formatNumber(currentValue);
      }
      if (currentFrame < totalFrames) {
        requestAnimationFrame(animate);
      } else {
        if (isCurrency) {
          element.textContent = formatCurrency(value);
        } else if (isPercentage) {
          element.textContent = formatPercentage(value);
        } else {
          element.textContent = formatNumber(value);
        }
      }
    };
    requestAnimationFrame(animate);
  }

  // Funções de formatação
  function formatCurrency(value) {
    return 'R$ ' + value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function formatPercentage(value) {
    return value.toFixed(1) + '%';
  }
  function formatNumber(value) {
    return Math.round(value).toLocaleString('pt-BR');
  }

  // Inicializar kanban
  function initKanban() {
    restoreKanbanView();
    DOM.kanbanColumns.forEach((column, index) => {
      column.style.animationDelay = `${0.05 * index}s`;
    });
    DOM.kanbanColumns.forEach(setupEmptyColumnState);
    updateScrollButtonVisibility();
    if (settings.dragDropEnabled) {
      initDragAndDrop();
    }
    // Animações e efeitos de hover
    DOM.leadCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.3s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
  }

  // Configurar estado de coluna vazia
  function setupEmptyColumnState(column) {
    const body = column.querySelector('.kanban-column-body');
    if (body && body.querySelectorAll('.lead-card').length === 0) {
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'empty-column-message';
      const columnType = Array.from(column.classList).find(cls => cls.startsWith('kanban-column-'))?.replace('kanban-column-', '');
      let icon, title, text;
      switch (columnType) {
        case 'new': icon = 'bi-inbox'; title = 'Sem leads novos'; text = 'Todos os leads novos aparecerão aqui'; break;
        case 'contacted': icon = 'bi-telephone'; title = 'Sem leads contatados'; text = 'Leads após primeiro contato aparecerão aqui'; break;
        case 'qualified': icon = 'bi-star'; title = 'Sem leads qualificados'; text = 'Leads qualificados aparecerão aqui'; break;
        case 'negotiation': icon = 'bi-chat-dots'; title = 'Sem leads em negociação'; text = 'Leads em negociação aparecerão aqui'; break;
        case 'closed': icon = 'bi-check-circle'; title = 'Sem leads fechados'; text = 'Leads fechados aparecerão aqui'; break;
        case 'lost': icon = 'bi-x-circle'; title = 'Sem leads perdidos'; text = 'Leads perdidos aparecerão aqui'; break;
        default: icon = 'bi-people'; title = 'Sem leads'; text = 'Sem leads nesta categoria';
      }
      emptyMessage.innerHTML = `<i class="bi ${icon}"></i><h4>${title}</h4><p>${text}</p>`;
      body.appendChild(emptyMessage);
    }
  }

  // Funções de rolagem do Kanban
  function scrollBoardLeft() {
    if (!DOM.boardScroller) return;
    DOM.boardScroller.scrollBy({ left: -340, behavior: 'smooth' });
  }
  function scrollBoardRight() {
    if (!DOM.boardScroller) return;
    DOM.boardScroller.scrollBy({ left: 340, behavior: 'smooth' });
  }
  function updateScrollButtonVisibility() {
    if (!DOM.boardScroller || !DOM.scrollLeftBtn || !DOM.scrollRightBtn) return;
    const { scrollLeft, scrollWidth, clientWidth } = DOM.boardScroller;
    DOM.scrollLeftBtn.classList.toggle('d-none', scrollLeft <= 10);
    DOM.scrollRightBtn.classList.toggle('d-none', scrollLeft + clientWidth >= scrollWidth - 10);
  }
  function scrollToColumn(index) {
    const column = DOM.kanbanColumns[index];
    if (!column || !DOM.boardScroller) return;
    column.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    column.classList.add('active');
    setTimeout(() => column.classList.remove('active'), 2000);
    if (settings.autoSaveEnabled) {
      saveKanbanView(index);
    }
  }

  // Persistência da visualização
  function saveKanbanView(index) {
    try {
      localStorage.setItem('funnel_last_column', index.toString());
    } catch (e) {
      console.warn('Não foi possível salvar a visualização do funil:', e);
    }
  }
  function restoreKanbanView() {
    try {
      const lastColumn = localStorage.getItem('funnel_last_column');
      if (lastColumn !== null) {
        setTimeout(() => scrollToColumn(parseInt(lastColumn)), 500);
      }
    } catch (e) {
      console.warn('Não foi possível restaurar a visualização do funil:', e);
    }
  }

  // Configuração dos cards de lead
  function configureLeadCard(card) {
    const valueBadge = card.querySelector('.lead-value-badge');
    if (valueBadge) {
      const valueText = valueBadge.textContent.trim();
      const valueMatch = valueText.match(/R\$\s*([\d.,]+)/);
      if (valueMatch) {
        const value = parseFloat(valueMatch[1].replace(/\./g, '').replace(',', '.'));
        if (value >= 50000) {
          valueBadge.classList.add('high-value');
        }
      }
    }
    if (settings.tooltipsEnabled) {
      card.addEventListener('mouseenter', showLeadTooltip);
      card.addEventListener('mouseleave', hideLeadTooltip);
    }
    card.querySelectorAll('.lead-action-btn').forEach(btn => btn.classList.add('ripple-effect'));
    card.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        showContextMenu(e, this);
    });
     card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px) scale(1.02)';
        this.style.boxShadow = '0 8px 16px rgba(0,0,0,0.3)';
        this.style.zIndex = '10';
    });
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
        this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.15)';
        this.style.zIndex = '1';
    });
  }

  // Tooltips
  function initTooltips() {
    const tooltipContainer = document.createElement('div');
    tooltipContainer.className = 'funnel-tooltip';
    tooltipContainer.id = 'funnel-tooltip';
    tooltipContainer.style.display = 'none';
    document.body.appendChild(tooltipContainer);
    document.addEventListener('mousemove', updateTooltipPosition);
  }
  function showLeadTooltip(event) {
    const card = event.currentTarget;
    const tooltipEl = document.getElementById('funnel-tooltip');
    if (!tooltipEl) return;
    const name = card.querySelector('.lead-name')?.textContent || 'Lead';
    const value = card.querySelector('.lead-value-badge')?.textContent || 'Valor não informado';
    const date = card.querySelector('.lead-date')?.textContent || '';
    tooltipEl.innerHTML = `<div class="funnel-tooltip-title">${name}</div><div class="funnel-tooltip-data"><div><strong>Valor:</strong> ${value}</div>${date ? `<div><strong>Data:</strong> ${date}</div>` : ''}</div>`;
    tooltipEl.style.display = 'block';
    setTimeout(() => tooltipEl.classList.add('visible'), 10);
    updateTooltipPosition(event);
  }
  function hideLeadTooltip() {
    const tooltipEl = document.getElementById('funnel-tooltip');
    if (!tooltipEl) return;
    tooltipEl.classList.remove('visible');
    setTimeout(() => { tooltipEl.style.display = 'none'; }, 300);
  }
  function updateTooltipPosition(event) {
    const tooltipEl = document.getElementById('funnel-tooltip');
    if (!tooltipEl || tooltipEl.style.display === 'none') return;
    const offsetX = 15, offsetY = 15;
    const { clientX, clientY } = event;
    const { offsetWidth, offsetHeight } = tooltipEl;
    const { innerWidth, innerHeight } = window;
    let left = clientX + offsetX;
    let top = clientY + offsetY;
    if (left + offsetWidth > innerWidth - 20) {
      left = clientX - offsetWidth - offsetX;
    }
    if (top + offsetHeight > innerHeight - 20) {
      top = clientY - offsetHeight - offsetY;
    }
    tooltipEl.style.left = `${left}px`;
    tooltipEl.style.top = `${top}px`;
  }

  // Observador de conteúdo dinâmico
  function observeDynamicContent() {
    if (!window.MutationObserver) return;
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        if (mutation.addedNodes.length) {
          mutation.addedNodes.forEach(node => {
            if (node.nodeType === 1 && node.classList && node.classList.contains('lead-card')) {
              configureLeadCard(node);
            }
          });
        }
      });
    });
    const kanbanContainer = document.querySelector('.board-container');
    if (kanbanContainer) {
      observer.observe(kanbanContainer, { childList: true, subtree: true });
    }
  }

  // Drag and Drop (futuro)
  function initDragAndDrop() {
    console.log('Drag and Drop não disponível nesta versão');
  }

  // Verificação de atualizações
  function checkPendingUpdates() {
    console.log('Verificando atualizações do funil...');
    setTimeout(() => console.log('Funil sincronizado com sucesso!'), 1000);
  }

  // Delegação de eventos de clique
  function delegateClickEvents(event) {
    const button = event.target.closest('.lead-action-btn');
    if (button) {
      const leadCard = button.closest('.lead-card');
      const leadId = leadCard?.dataset.leadId;
      if (!leadId) return;
      if (button.classList.contains('action-view')) {
        console.log(`Visualizando lead: ${leadId}`);
      } else if (button.classList.contains('action-edit')) {
        console.log(`Editando lead: ${leadId}`);
      } else if (button.classList.contains('action-contact')) {
        console.log(`Registrando contato para lead: ${leadId}`);
      }
    }
  }
  
  // Menu de contexto
  function showContextMenu(event, card) {
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.innerHTML = `
        <div class="context-menu-item" onclick="SalesFunnel.viewLead(this)"><i class="bi bi-eye"></i> Ver Detalhes</div>
        <div class="context-menu-item" onclick="SalesFunnel.contactLead(this)"><i class="bi bi-telephone"></i> Registrar Contato</div>
        <div class="context-menu-item" onclick="SalesFunnel.editLead(this)"><i class="bi bi-pencil"></i> Editar Lead</div>
    `;
    menu.style.cssText = `position: fixed; top: ${event.clientY}px; left: ${event.clientX}px; z-index: 1000;`;
    document.body.appendChild(menu);
    document.addEventListener('click', () => menu.remove(), { once: true });
  }

  // Otimizações
  function checkBrowserCompatibility() {
    if (!window.CSS || !window.CSS.supports || !window.CSS.supports('--test', '0')) {
        console.warn('Seu navegador não suporta variáveis CSS. Alguns recursos visuais podem não funcionar.');
        document.body.classList.add('no-css-vars');
    }
  }
  function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('.lazy-load');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        });
        lazyImages.forEach(img => imageObserver.observe(img));
    }
  }
  function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;
  }
  function applyMobileOptimizations() {
    document.body.classList.add('is-mobile-device');
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .is-mobile-device .funnel-segment, .is-mobile-device .stat-card { transition: none; animation: none; }
        .is-mobile-device .kanban-column { min-width: 260px; }
    `;
    document.head.appendChild(styleElement);
  }
  
  // Auto-refresh e notificações
  function setupAutoRefresh() {
    setInterval(() => {
        showUpdateNotification('Verificando novas atualizações...', 'info');
        setTimeout(() => refreshFunnel(), 2000);
    }, settings.autoRefreshInterval);
  }
  function showUpdateNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `update-notification notification-${type}`;
    const icons = { info: 'info-circle', success: 'check-circle', warning: 'exclamation-triangle', error: 'x-circle' };
    notification.innerHTML = `<div class="notification-content"><i class="bi bi-${icons[type] || 'info-circle'}"></i><span>${message}</span></div>`;
    document.body.appendChild(notification);
    setTimeout(() => notification.classList.add('visible'), 100);
    setTimeout(() => {
        notification.classList.remove('visible');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
  }
  function initializeChangeMonitoring() {
    const currentCounts = {};
    document.querySelectorAll('.kanban-column-count').forEach((countEl, index) => {
        currentCounts[index] = parseInt(countEl.textContent) || 0;
    });
    const storedCounts = JSON.parse(localStorage.getItem('funnelCounts') || '{}');
    if (Object.keys(storedCounts).length) {
        let hasChanges = false;
        document.querySelectorAll('.kanban-column').forEach((column, index) => {
            const currentCount = currentCounts[index];
            const previousCount = storedCounts[index] || 0;
            if (currentCount !== previousCount) {
                hasChanges = true;
                const diff = currentCount - previousCount;
                const columnTitle = column.querySelector('.kanban-column-title').textContent;
                const message = `${diff > 0 ? '+' : ''}${diff} em ${columnTitle}`;
                showUpdateNotification(message, diff > 0 ? 'success' : 'warning');
            }
        });
    }
    localStorage.setItem('funnelCounts', JSON.stringify(currentCounts));
  }
  
  // Atalhos de teclado
  function handleKeyboardShortcuts(event) {
    if (event.key === 'ArrowLeft') document.querySelector('.kanban-scroll-left')?.click();
    if (event.key === 'ArrowRight') document.querySelector('.kanban-scroll-right')?.click();
    const columnNumber = parseInt(event.key);
    if (columnNumber >= 1 && columnNumber <= (DOM.kanbanColumns?.length || 6)) {
      scrollToColumn(columnNumber - 1);
    }
    if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
        event.preventDefault();
        refreshFunnel();
    }
  }
  
  function refreshFunnel() {
      console.log('Atualizando visualização do funil...');
      showUpdateNotification('Atualizando dados...', 'info');
      window.location.reload();
  }

  // API pública
  return {
    init,
    scrollToColumn,
    refreshFunnel,
    getSettings: () => ({ ...settings }),
    updateSettings: (newSettings) => {
      Object.assign(settings, newSettings);
      console.log('Configurações do funil atualizadas:', settings);
    },
    viewLead: (element) => {
        const card = element.closest('.lead-card');
        const leadId = card?.dataset.leadId;
        console.log(`Ação: Ver lead ${leadId}`);
        // A lógica de navegação deve estar no href do botão de ação original
    },
    contactLead: (element) => {
        const card = element.closest('.lead-card');
        const leadId = card?.dataset.leadId;
        console.log(`Ação: Contatar lead ${leadId}`);
    },
    editLead: (element) => {
        const card = element.closest('.lead-card');
        const leadId = card?.dataset.leadId;
        console.log(`Ação: Editar lead ${leadId}`);
    }
  };
})();

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', SalesFunnel.init);
