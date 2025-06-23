/**
 * Responsive Handler for Lions CRM
 * 
 * Este script melhora a experiência responsiva da aplicação,
 * ajustando elementos em diferentes tamanhos de tela.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Variáveis úteis
    const isMobile = window.innerWidth < 768;
    const isTablet = window.innerWidth >= 768 && window.innerWidth < 992;
    const isDesktop = window.innerWidth >= 992;
    
    // Função para ajustar elementos baseado no tamanho da tela
    function adjustForScreenSize() {
        // Ajustar altura dos cards para que tenham tamanho uniforme em cada linha
        const equalizeCardHeights = function(selector) {
            const cards = document.querySelectorAll(selector);
            if (cards.length === 0) return;
            
            // Reset heights
            cards.forEach(card => {
                card.style.height = 'auto';
            });
            
            if (window.innerWidth >= 768) {
                // Agrupar cards pela mesma linha (com base na posição Y)
                const rows = {};
                cards.forEach(card => {
                    const rect = card.getBoundingClientRect();
                    const rowPosition = Math.floor(rect.top);
                    if (!rows[rowPosition]) rows[rowPosition] = [];
                    rows[rowPosition].push(card);
                });
                
                // Definir a mesma altura para cards na mesma linha
                Object.values(rows).forEach(rowCards => {
                    const maxHeight = Math.max(...rowCards.map(c => c.offsetHeight));
                    rowCards.forEach(c => c.style.height = maxHeight + 'px');
                });
            }
        };
        
        // Ajustar tamanho dos cards de workflow, campanhas, etc
        equalizeCardHeights('.workflow-card');
        equalizeCardHeights('.campaign-card');
        equalizeCardHeights('.dashboard-stat-card');
        
        // Ajustar o posicionamento de dropdowns em mobile
        const adjustDropdownPosition = function() {
            if (isMobile) {
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    menu.classList.add('dropdown-menu-mobile');
                    menu.style.position = 'static';
                    menu.style.width = '100%';
                });
            }
        };
        adjustDropdownPosition();
        
        // Selecionar colunas de dados que podem precisar de rolagem horizontal
        const adjustDataTables = function() {
            document.querySelectorAll('table.table').forEach(table => {
                if (!table.parentElement.classList.contains('table-responsive')) {
                    const wrapper = document.createElement('div');
                    wrapper.classList.add('table-responsive');
                    table.parentNode.insertBefore(wrapper, table);
                    wrapper.appendChild(table);
                }
            });
        };
        adjustDataTables();
        
        // Aplicar ajustes específicos para dispositivos móveis
        if (isMobile) {
            // Ajustar padding em contêineres para economizar espaço
            document.querySelectorAll('.container, .container-fluid').forEach(container => {
                container.style.paddingLeft = '0.5rem';
                container.style.paddingRight = '0.5rem';
            });
            
            // Simplificar cabeçalhos em dispositivos pequenos
            document.querySelectorAll('.page-header').forEach(header => {
                header.classList.add('mobile-simplified');
            });
        }
    }
    
    // Aplicar ajustes iniciais
    adjustForScreenSize();
    
    // Reajustar quando a janela for redimensionada
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(adjustForScreenSize, 250);
    });
    
    // Ajustar formulários para melhor experiência em dispositivos móveis
    if (isMobile) {
        // Evitar zoom em campos de formulário no iOS
        document.querySelectorAll('input, select, textarea').forEach(input => {
            if (input.type !== 'checkbox' && input.type !== 'radio') {
                input.style.fontSize = '16px';
            }
        });
        
        // Tornar botões maiores para melhor experiência touch
        document.querySelectorAll('.btn, button:not(.navbar-toggler)').forEach(btn => {
            btn.classList.add('touch-friendly');
        });
    }
    
    // Ajustar modais em dispositivos móveis
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            if (isMobile) {
                // Certificar que o modal ocupa quase toda a tela em dispositivos móveis
                const modalDialog = this.querySelector('.modal-dialog');
                modalDialog.classList.add('mobile-modal');
                
                // Ajustar posição do overlay para cobrir tudo
                setTimeout(() => {
                    const modalBackdrop = document.querySelector('.modal-backdrop');
                    if (modalBackdrop) {
                        modalBackdrop.style.width = '100%';
                        modalBackdrop.style.height = '100%';
                    }
                }, 10);
            }
        });
    });
    
    // Melhorar a rolagem em dispositivos touch
    if ('ontouchstart' in window) {
        document.querySelectorAll('.sidebar, .overflow-auto').forEach(element => {
            element.style.webkitOverflowScrolling = 'touch';
        });
    }
});
