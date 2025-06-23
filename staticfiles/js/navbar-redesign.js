/**
 * NAVBAR INTERACTIONS - ROAR CRM
 * Funcionalidades interativas para o navbar redesenhado
 */

document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.getElementById('mainNavbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    // Scroll effect para o navbar
    function handleNavbarScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
    
    // Adiciona listener para scroll
    window.addEventListener('scroll', handleNavbarScroll);
    
    // Auto-collapse do menu mobile quando clicar em um link
    const mobileNavLinks = document.querySelectorAll('.navbar-nav .nav-link:not(.dropdown-toggle)');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    hide: true
                });
            }
        });
    });
    
    // Highlight do item ativo baseado na URL atual
    function setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.main-nav .nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href');
            
            if (href && currentPath.includes(href.split('/')[1])) {
                link.classList.add('active');
            }
        });
    }
    
    // Chama a função ao carregar a página
    setActiveNavItem();
    
    // Smooth hover effects para dropdowns
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        const dropdownMenu = toggle.nextElementSibling;
        
        if (dropdownMenu) {
            let hoverTimeout;
            
            // Mouse enter
            toggle.addEventListener('mouseenter', () => {
                clearTimeout(hoverTimeout);
                if (window.innerWidth >= 992) {
                    hoverTimeout = setTimeout(() => {
                        const bsDropdown = new bootstrap.Dropdown(toggle);
                        bsDropdown.show();
                    }, 150);
                }
            });
            
            // Mouse leave
            const dropdownContainer = toggle.closest('.dropdown');
            dropdownContainer.addEventListener('mouseleave', () => {
                clearTimeout(hoverTimeout);
                if (window.innerWidth >= 992) {
                    const bsDropdown = bootstrap.Dropdown.getInstance(toggle);
                    if (bsDropdown) {
                        bsDropdown.hide();
                    }
                }
            });
        }
    });
    
    // Loading animation para links
    function addLoadingAnimation(link) {
        link.classList.add('loading');
        
        // Remove loading após 2 segundos (ou quando a página carregar)
        setTimeout(() => {
            link.classList.remove('loading');
        }, 2000);
    }
    
    // Adiciona loading animation aos links principais
    const mainNavLinks = document.querySelectorAll('.main-nav .nav-link:not(.dropdown-toggle)');
    mainNavLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Não adiciona loading se for um link para modal ou ação JS
            const href = this.getAttribute('href');
            if (href && !href.startsWith('#') && !href.includes('javascript:')) {
                addLoadingAnimation(this);
            }
        });
    });
    
    // Notification indicator (exemplo para futuras notificações)
    function addNotificationBadge(element, count) {
        const existingBadge = element.querySelector('.notification-badge');
        if (existingBadge) {
            existingBadge.remove();
        }
        
        if (count > 0) {
            const badge = document.createElement('span');
            badge.className = 'notification-badge';
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.cssText = `
                position: absolute;
                top: -5px;
                right: -5px;
                background: #dc3545;
                color: white;
                border-radius: 50%;
                width: 18px;
                height: 18px;
                font-size: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                z-index: 10;
            `;
            
            element.style.position = 'relative';
            element.appendChild(badge);
        }
    }
    
    // Exemplo de uso da notification badge
    // addNotificationBadge(document.querySelector('.quick-actions .nav-link'), 3);
    
    // Responsive behavior adjustments
    function handleResize() {
        const isMobile = window.innerWidth < 992;
        
        // Remove hover effects em mobile
        dropdownToggles.forEach(toggle => {
            if (isMobile) {
                toggle.removeEventListener('mouseenter', () => {});
                toggle.closest('.dropdown').removeEventListener('mouseleave', () => {});
            }
        });
    }
    
    window.addEventListener('resize', handleResize);
    handleResize(); // Chama na inicialização
    
    // Breadcrumb dinâmico (opcional)
    function updateBreadcrumb() {
        const currentPath = window.location.pathname;
        const breadcrumbContainer = document.querySelector('.dynamic-breadcrumb');
        
        if (breadcrumbContainer) {
            const pathSegments = currentPath.split('/').filter(segment => segment);
            const breadcrumbItems = pathSegments.map((segment, index) => {
                const isLast = index === pathSegments.length - 1;
                const url = '/' + pathSegments.slice(0, index + 1).join('/') + '/';
                
                return `
                    <li class="breadcrumb-item ${isLast ? 'active' : ''}">
                        ${isLast ? segment : `<a href="${url}">${segment}</a>`}
                    </li>
                `;
            }).join('');
            
            breadcrumbContainer.innerHTML = `
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb">
                        <li class="breadcrumb-item"><a href="/">Início</a></li>
                        ${breadcrumbItems}
                    </ol>
                </nav>
            `;
        }
    }
    
    // Keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // ESC fecha todos os dropdowns
        if (e.key === 'Escape') {
            const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
            openDropdowns.forEach(dropdown => {
                const toggle = dropdown.previousElementSibling;
                const bsDropdown = bootstrap.Dropdown.getInstance(toggle);
                if (bsDropdown) {
                    bsDropdown.hide();
                }
            });
        }
        
        // Tab navigation melhorada
        if (e.key === 'Tab') {
            const focusedElement = document.activeElement;
            if (focusedElement.classList.contains('dropdown-toggle')) {
                // Implementar navegação por tab nos dropdowns se necessário
            }
        }
    });
    
    // Performance optimization: debounce scroll handler
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Aplica debounce ao scroll handler
    window.removeEventListener('scroll', handleNavbarScroll);
    window.addEventListener('scroll', debounce(handleNavbarScroll, 10));
    
    // Analytics tracking (opcional - para futura implementação)
    function trackNavigation(linkText, linkUrl) {
        // console.log('Navigation tracked:', linkText, linkUrl);
        // Aqui você pode integrar com Google Analytics ou outro sistema
    }
    
    // Adiciona tracking aos links principais
    const trackableLinks = document.querySelectorAll('.main-nav .nav-link, .dropdown-item');
    trackableLinks.forEach(link => {
        link.addEventListener('click', function() {
            const linkText = this.textContent.trim();
            const linkUrl = this.getAttribute('href');
            trackNavigation(linkText, linkUrl);
        });
    });
});

// Utility function para adicionar classes CSS dinamicamente
function addNavbarUtilityClass(className) {
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        navbar.classList.add(className);
    }
}

// Utility function para remover classes CSS
function removeNavbarUtilityClass(className) {
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        navbar.classList.remove(className);
    }
}

// Export das funções para uso global se necessário
window.RoarNavbar = {
    addNotificationBadge: addNotificationBadge,
    addUtilityClass: addNavbarUtilityClass,
    removeUtilityClass: removeNavbarUtilityClass
};
