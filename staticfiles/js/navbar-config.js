/**
 * NAVBAR CONFIGURATION - ROAR CRM
 * Arquivo de configuração para personalização do navbar
 */

window.NavbarConfig = {
    // Configurações de tema
    theme: {
        // Cores principais
        colors: {
            primary: '#d4af37',
            primaryLight: '#e6c158',
            primaryDark: '#aa8c2c',
            dark: '#121212',
            darkLighter: '#1e1e1e',
            text: '#e0e0e0',
            textMuted: '#aaaaaa'
        },
        
        // Animações
        animations: {
            enabled: true,
            duration: 300,
            easing: 'ease',
            reducedMotion: false // Será detectado automaticamente
        },
        
        // Layout
        layout: {
            height: 70,
            mobileHeight: 60,
            sticky: true,
            blur: true,
            shadow: true
        }
    },
    
    // Configurações de comportamento
    behavior: {
        // Auto-collapse em mobile
        autoCollapse: true,
        
        // Hover dropdowns em desktop
        hoverDropdowns: true,
        hoverDelay: 150,
        
        // Scroll effects
        scrollEffects: true,
        scrollThreshold: 50,
        
        // Keyboard navigation
        keyboardNav: true,
        
        // Active state detection
        autoActiveState: true
    },
    
    // Configurações de performance
    performance: {
        // Debounce para scroll
        scrollDebounce: 10,
        
        // Lazy loading
        lazyLoad: true,
        
        // Will-change optimization
        willChange: true
    },
    
    // Configurações de acessibilidade
    accessibility: {
        // ARIA labels
        ariaLabels: {
            mainNav: 'Navegação principal',
            userMenu: 'Menu do usuário',
            quickActions: 'Ações rápidas',
            dropdownToggle: 'Abrir menu',
            mobileToggle: 'Abrir navegação'
        },
        
        // Focus management
        focusManagement: true,
        
        // Screen reader support
        screenReader: true,
        
        // High contrast support
        highContrast: true
    },
    
    // Configurações de notificações
    notifications: {
        enabled: true,
        maxCount: 99,
        animation: 'pulse',
        position: 'top-right'
    },
    
    // Configurações de analytics (para futura implementação)
    analytics: {
        enabled: false,
        trackClicks: true,
        trackHovers: false,
        trackScrolling: false
    },
    
    // Breakpoints responsivos
    breakpoints: {
        mobile: 575.98,
        tablet: 767.98,
        desktop: 991.98,
        large: 1199.98
    },
    
    // Classes CSS customizáveis
    classes: {
        navbar: 'navbar-custom',
        navbarScrolled: 'navbar-scrolled',
        navbarLoading: 'navbar-loading',
        navbarAlert: 'navbar-alert-mode',
        navbarSuccess: 'navbar-success-mode',
        dropdownOpen: 'dropdown-open',
        mobileOpen: 'mobile-nav-open'
    },
    
    // Seletores DOM
    selectors: {
        navbar: '#mainNavbar',
        navbarToggler: '.navbar-toggler',
        navbarCollapse: '.navbar-collapse',
        mainNav: '.main-nav',
        userNav: '.user-nav',
        dropdownToggle: '.dropdown-toggle',
        dropdownMenu: '.dropdown-menu',
        navLink: '.nav-link',
        dropdownItem: '.dropdown-item'
    },
    
    // URLs da aplicação (serão sobrescritas via Django)
    urls: {
        dashboard: '/',
        leads: '/leads/',
        automacao: '/automacao/',
        ferramentas: '/utils/',
        gestao: '/gerencia/',
        logout: '/logout/'
    },
    
    // Mensagens localizadas
    messages: {
        loading: 'Carregando...',
        error: 'Erro ao carregar',
        noNotifications: 'Nenhuma notificação',
        menuClosed: 'Menu fechado',
        menuOpened: 'Menu aberto'
    },
    
    // Funcionalidades experimentais
    experimental: {
        // PWA integration
        pwa: false,
        
        // Service Worker cache
        swCache: false,
        
        // Offline mode
        offline: false,
        
        // Real-time notifications
        realtime: false
    }
};

/**
 * Função para atualizar configurações
 * @param {Object} newConfig - Novas configurações
 */
window.updateNavbarConfig = function(newConfig) {
    window.NavbarConfig = {
        ...window.NavbarConfig,
        ...newConfig
    };
    
    // Reinicializar navbar com novas configurações
    if (window.RoarNavbar && window.RoarNavbar.reinitialize) {
        window.RoarNavbar.reinitialize();
    }
};

/**
 * Função para resetar configurações para padrão
 */
window.resetNavbarConfig = function() {
    location.reload(); // Recarrega a página para voltar ao padrão
};

/**
 * Função para detectar configurações do sistema
 */
window.detectSystemPreferences = function() {
    const config = {};
    
    // Detectar preferência de motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        config.theme = {
            ...window.NavbarConfig.theme,
            animations: {
                ...window.NavbarConfig.theme.animations,
                reducedMotion: true,
                enabled: false
            }
        };
    }
    
    // Detectar high contrast
    if (window.matchMedia('(prefers-contrast: high)').matches) {
        config.accessibility = {
            ...window.NavbarConfig.accessibility,
            highContrast: true
        };
    }
    
    // Detectar dark mode preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // Já estamos em dark mode por padrão
    }
    
    return config;
};

/**
 * Função para aplicar tema personalizado
 * @param {string} themeName - Nome do tema ('dark', 'light', 'auto')
 */
window.applyNavbarTheme = function(themeName) {
    const navbar = document.querySelector(window.NavbarConfig.selectors.navbar);
    if (!navbar) return;
    
    // Remover classes de tema existentes
    navbar.classList.remove('navbar-theme-dark', 'navbar-theme-light', 'navbar-theme-auto');
    
    // Aplicar novo tema
    switch (themeName) {
        case 'dark':
            navbar.classList.add('navbar-theme-dark');
            break;
        case 'light':
            navbar.classList.add('navbar-theme-light');
            break;
        case 'auto':
            navbar.classList.add('navbar-theme-auto');
            break;
    }
};

// Inicializar configurações baseadas no sistema
document.addEventListener('DOMContentLoaded', function() {
    const systemConfig = window.detectSystemPreferences();
    if (Object.keys(systemConfig).length > 0) {
        window.updateNavbarConfig(systemConfig);
    }
});

// Export para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.NavbarConfig;
}
