/**
 * Funnel Sales Optimizer
 * Otimizações para o Funil de Vendas do Lions CRM
 * Versão: 1.0
 * Data: 13/06/2025
 */

document.addEventListener('DOMContentLoaded', function() {
    // Verificar compatibilidade do navegador
    checkBrowserCompatibility();
    
    // Implementar lazy loading para imagens
    setupLazyLoading();
    
    // Otimizar scrolling do kanban
    optimizeKanbanScrolling();
    
    // Detectar dispositivo móvel para otimizações específicas
    if (isMobileDevice()) {
        applyMobileOptimizations();
    }
});

/**
 * Verifica a compatibilidade do navegador e aplica polyfills se necessário
 */
function checkBrowserCompatibility() {
    // Verificar suporte a CSS variables
    const isCSSVarSupported = window.CSS && window.CSS.supports && window.CSS.supports('--test', '0');
    
    if (!isCSSVarSupported) {
        console.warn('Seu navegador não suporta variáveis CSS. Algumas funcionalidades visuais podem não funcionar corretamente.');
        document.body.classList.add('no-css-vars');
        applyFallbackStyles();
    }
    
    // Verificar suporte a Grid Layout
    const isGridSupported = window.CSS && window.CSS.supports && (
        window.CSS.supports('display', 'grid') || 
        window.CSS.supports('display', '-ms-grid')
    );
    
    if (!isGridSupported) {
        console.warn('Seu navegador não suporta CSS Grid. O layout poderá ser exibido de forma diferente.');
        document.body.classList.add('no-grid-support');
    }
    
    // Log do navegador para debug
    const userAgent = navigator.userAgent;
    console.log('Navegador detectado:', userAgent);
}

/**
 * Aplica estilos alternativos para navegadores sem suporte a variáveis CSS
 */
function applyFallbackStyles() {
    const fallbackStyles = document.createElement('style');
    fallbackStyles.textContent = `
        .funnel-page { background-color: #222; color: white; }
        .kanban-column { background-color: #2a2a2a; border: 1px solid #333; }
        .lead-card { background-color: #333; }
        .stat-card { background-color: #2d2d2d; }
        
        .kanban-column-new .kanban-column-header { border-top: 3px solid #007bff; }
        .kanban-column-contacted .kanban-column-header { border-top: 3px solid #17a2b8; }
        .kanban-column-qualified .kanban-column-header { border-top: 3px solid #ffc107; }
        .kanban-column-negotiation .kanban-column-header { border-top: 3px solid #fd7e14; }
        .kanban-column-closed .kanban-column-header { border-top: 3px solid #28a745; }
        .kanban-column-lost .kanban-column-header { border-top: 3px solid #dc3545; }
    `;
    document.head.appendChild(fallbackStyles);
}

/**
 * Configura lazy loading para melhorar performance
 */
function setupLazyLoading() {
    // Verificar se o navegador suporta IntersectionObserver
    if ('IntersectionObserver' in window) {
        // Imagens e avatares que serão carregados sob demanda
        const lazyImages = document.querySelectorAll('.lazy-load');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback para navegadores sem suporte ao IntersectionObserver
        console.log('IntersectionObserver não suportado. Lazy loading não será aplicado.');
    }
}

/**
 * Otimiza o scrolling do kanban para melhor performance
 */
function optimizeKanbanScrolling() {
    const scrollContainer = document.querySelector('.board-scroller');
    
    if (scrollContainer) {
        // Usar passive listener para melhorar performance do scroll
        scrollContainer.addEventListener('scroll', () => {
            // Pode ser usado para efeitos durante o scroll
        }, { passive: true });
        
        // Adicionar controles de navegação para facilitar em telas grandes
        addScrollControls(scrollContainer);
    }
}

/**
 * Adiciona controles de navegação para facilitar o scroll horizontal
 */
function addScrollControls(container) {
    // Criar elementos de controle
    const leftControl = document.createElement('button');
    leftControl.className = 'kanban-scroll-control kanban-scroll-left';
    leftControl.innerHTML = '<i class="bi bi-chevron-left"></i>';
    
    const rightControl = document.createElement('button');
    rightControl.className = 'kanban-scroll-control kanban-scroll-right';
    rightControl.innerHTML = '<i class="bi bi-chevron-right"></i>';
    
    // Adicionar à página
    const kanbanBoard = document.querySelector('.kanban-board');
    kanbanBoard.appendChild(leftControl);
    kanbanBoard.appendChild(rightControl);
    
    // Adicionar eventos
    leftControl.addEventListener('click', () => {
        container.scrollBy({ left: -300, behavior: 'smooth' });
    });
    
    rightControl.addEventListener('click', () => {
        container.scrollBy({ left: 300, behavior: 'smooth' });
    });
    
    // Mostrar/esconder controles baseado na posição do scroll
    container.addEventListener('scroll', () => {
        const isAtStart = container.scrollLeft <= 20;
        const isAtEnd = container.scrollLeft + container.clientWidth >= container.scrollWidth - 20;
        
        leftControl.style.opacity = isAtStart ? '0.3' : '1';
        leftControl.style.pointerEvents = isAtStart ? 'none' : 'auto';
        
        rightControl.style.opacity = isAtEnd ? '0.3' : '1';
        rightControl.style.pointerEvents = isAtEnd ? 'none' : 'auto';
    });
}

/**
 * Detecta se o usuário está acessando de um dispositivo móvel
 */
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
        || window.innerWidth < 768;
}

/**
 * Aplica otimizações específicas para dispositivos móveis
 */
function applyMobileOptimizations() {
    // Adicionar classe para estilos específicos
    document.body.classList.add('is-mobile-device');
    
    // Simplificar alguns elementos para melhorar performance
    document.querySelectorAll('.lead-card').forEach(card => {
        card.classList.add('simplified');
    });
    
    // Reduzir efeitos visuais em dispositivos móveis
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .is-mobile-device .funnel-segment {
            transition: none;
        }
        
        .is-mobile-device .kanban-column {
            min-width: 260px;
        }
        
        .is-mobile-device .stat-card {
            animation: none;
        }
    `;
    document.head.appendChild(styleElement);
}
