/**
 * NAVBAR INTERACTIONS V2 - ROAR CRM
 * Funcionalidades interativas para o navbar redesenhado com melhor contraste
 */

document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.getElementById('mainNavbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    // Configurações
    const config = {
        scrollThreshold: 50,
        animationDuration: 300,
        mobileBreakpoint: 992,
        autoCollapseDelay: 200
    };
    
    // ===============================================
    // SCROLL EFFECTS
    // ===============================================
    
    let scrollTimeout;
    function handleNavbarScroll() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            if (window.scrollY > config.scrollThreshold) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }, 10);
    }
    
    // Debounced scroll listener
    window.addEventListener('scroll', handleNavbarScroll, { passive: true });
    
    // ===============================================
    // MOBILE NAVIGATION
    // ===============================================
    
    // Auto-collapse do menu mobile quando clicar em um link
    const mobileNavLinks = document.querySelectorAll('.navbar-nav .nav-link:not(.dropdown-toggle)');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (window.innerWidth < config.mobileBreakpoint && navbarCollapse.classList.contains('show')) {
                setTimeout(() => {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    }
                }, config.autoCollapseDelay);
            }
        });
    });
    
    // Melhor handling do mobile toggle
    if (navbarToggler) {
        navbarToggler.addEventListener('click', () => {
            navbar.classList.toggle('menu-open');
        });
    }
    
    // ===============================================
    // DROPDOWN INTERACTIONS
    // ===============================================
    
    // Enhanced dropdown behavior para desktop
    dropdownToggles.forEach(toggle => {
        const dropdownMenu = toggle.nextElementSibling;
        if (!dropdownMenu) return;
        
        let hideTimeout;
        
        // Show on hover (desktop only)
        if (window.innerWidth >= config.mobileBreakpoint) {
            toggle.parentElement.addEventListener('mouseenter', () => {
                clearTimeout(hideTimeout);
                if (!toggle.classList.contains('show')) {
                    toggle.click();
                }
            });
            
            toggle.parentElement.addEventListener('mouseleave', () => {
                hideTimeout = setTimeout(() => {
                    if (toggle.classList.contains('show')) {
                        toggle.click();
                    }
                }, 300);
            });
        }
    });
    
    // ===============================================
    // ACTIVE STATE MANAGEMENT
    // ===============================================
    
    function setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.main-nav .nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href');
            
            if (href) {
                // Melhor detecção de URL ativa
                const linkPath = new URL(href, window.location.origin).pathname;
                if (currentPath === linkPath || 
                    (linkPath !== '/' && currentPath.startsWith(linkPath))) {
                    link.classList.add('active');
                }
            }
        });
        
        // Marca dropdown como ativo se algum item interno estiver ativo
        document.querySelectorAll('.dropdown-menu .dropdown-item').forEach(item => {
            const href = item.getAttribute('href');
            if (href) {
                const linkPath = new URL(href, window.location.origin).pathname;
                if (currentPath === linkPath || 
                    (linkPath !== '/' && currentPath.startsWith(linkPath))) {
                    const parentDropdown = item.closest('.dropdown').querySelector('.dropdown-toggle');
                    if (parentDropdown) {
                        parentDropdown.classList.add('active');
                    }
                }
            }
        });
    }
    
    setActiveNavItem();
    
    // ===============================================
    // KEYBOARD NAVIGATION
    // ===============================================
    
    document.addEventListener('keydown', (e) => {
        // ESC para fechar dropdowns
        if (e.key === 'Escape') {
            dropdownToggles.forEach(toggle => {
                if (toggle.classList.contains('show')) {
                    toggle.click();
                }
            });
            
            // Fechar menu mobile
            if (navbarCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
        }
    });
    
    // ===============================================
    // LOADING STATES
    // ===============================================
    
    function showNavbarLoading() {
        navbar.classList.add('loading');
    }
    
    function hideNavbarLoading() {
        navbar.classList.remove('loading');
    }
    
    // Intercepta clicks em links para mostrar loading
    document.querySelectorAll('.nav-link, .dropdown-item').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href && href !== '#' && !href.startsWith('javascript:')) {
                showNavbarLoading();
                
                // Remove loading após 3 segundos como fallback
                setTimeout(() => {
                    hideNavbarLoading();
                }, 3000);
            }
        });
    });
    
    // Remove loading quando a página carregar
    window.addEventListener('load', hideNavbarLoading);
    
    // ===============================================
    // NOTIFICATION SYSTEM
    // ===============================================
    
    function updateNotificationBadge(count) {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }
    
    // ===============================================
    // SEARCH FUNCTIONALITY (placeholder)
    // ===============================================
    
    const searchInput = document.querySelector('.navbar-search input');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = e.target.value.trim();
                if (query.length >= 3) {
                    // Implementar busca aqui
                    console.log('Buscar por:', query);
                }
            }, 500);
        });
    }
    
    // ===============================================
    // THEME SWITCHING (preparação para futuro)
    // ===============================================
    
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-navbar-theme', theme);
        localStorage.setItem('navbar-theme', theme);
    }
    
    function initTheme() {
        const savedTheme = localStorage.getItem('navbar-theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
        applyTheme(theme);
    }
    
    initTheme();
    
    // ===============================================
    // PERFORMANCE OPTIMIZATIONS
    // ===============================================
    
    // Intersection Observer para animações
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const navObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observa elementos da navegação
    document.querySelectorAll('.nav-item, .user-nav > *').forEach(el => {
        navObserver.observe(el);
    });
    
    // ===============================================
    // RESPONSIVE HANDLING
    // ===============================================
    
    function handleResize() {
        const isMobile = window.innerWidth < config.mobileBreakpoint;
        
        if (!isMobile && navbarCollapse.classList.contains('show')) {
            const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        }
        
        // Ajusta dropdown behavior baseado no tamanho da tela
        dropdownToggles.forEach(toggle => {
            if (isMobile) {
                toggle.removeAttribute('data-bs-auto-close');
            } else {
                toggle.setAttribute('data-bs-auto-close', 'outside');
            }
        });
    }
    
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    });
    
    handleResize(); // Chamada inicial
    
    // ===============================================
    // ACCESSIBILITY ENHANCEMENTS
    // ===============================================
    
    // Melhor suporte para navegação por teclado
    document.querySelectorAll('.nav-link, .dropdown-item').forEach(link => {
        link.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                link.click();
            }
        });
    });
    
    // Announce para screen readers
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
    
    // ===============================================
    // UTILITY FUNCTIONS
    // ===============================================
    
    function isMobileDevice() {
        return window.innerWidth < config.mobileBreakpoint;
    }
    
    function showSuccess(message) {
        navbar.classList.add('success');
        setTimeout(() => {
            navbar.classList.remove('success');
        }, 3000);
        
        if (message) {
            announceToScreenReader(message);
        }
    }
    
    function showAlert(message) {
        navbar.classList.add('alert');
        setTimeout(() => {
            navbar.classList.remove('alert');
        }, 5000);
        
        if (message) {
            announceToScreenReader(message);
        }
    }
    
    // ===============================================
    // GLOBAL API
    // ===============================================
    
    // Expõe funções globalmente para uso em outras partes do sistema
    window.NavbarAPI = {
        setActiveItem: setActiveNavItem,
        showLoading: showNavbarLoading,
        hideLoading: hideNavbarLoading,
        updateNotifications: updateNotificationBadge,
        showSuccess: showSuccess,
        showAlert: showAlert,
        applyTheme: applyTheme,
        isMobile: isMobileDevice
    };
    
    // ===============================================
    // INITIALIZATION COMPLETE
    // ===============================================
    
    console.log('✅ Navbar V2 inicializado com sucesso');
    
    // Dispatch custom event
    const navbarReadyEvent = new CustomEvent('navbarReady', {
        detail: { version: '2.0', api: window.NavbarAPI }
    });
    document.dispatchEvent(navbarReadyEvent);
});
