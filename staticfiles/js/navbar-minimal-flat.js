/**
 * NAVBAR MINIMAL FLAT - JavaScript Utilities
 * Funcionalidades extras para o navbar
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        const navbar = document.getElementById('navbarContent');
        const toggler = document.querySelector('.navbar-toggler');
        
        if (navbar && navbar.classList.contains('show')) {
            if (!navbar.contains(event.target) && !toggler.contains(event.target)) {
                const bsCollapse = bootstrap.Collapse.getOrCreateInstance(navbar);
                bsCollapse.hide();
            }
        }
    });
      // Add smooth scroll behavior to navbar links
    const smoothScrollLinks = document.querySelectorAll('.nav-link[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#') && href.length > 1) {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Improve dropdown behavior on mobile
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.addEventListener('click', function() {
            // Close mobile menu after selection
            const navbar = document.getElementById('navbarContent');
            if (navbar && navbar.classList.contains('show')) {
                setTimeout(() => {
                    const bsCollapse = bootstrap.Collapse.getOrCreateInstance(navbar);
                    bsCollapse.hide();
                }, 150);
            }
        });
    });
    
    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close any open dropdowns
            const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
            openDropdowns.forEach(dropdown => {
                const toggle = dropdown.previousElementSibling;
                if (toggle) {
                    const bsDropdown = bootstrap.Dropdown.getOrCreateInstance(toggle);
                    bsDropdown.hide();
                }
            });
            
            // Close mobile menu
            const navbar = document.getElementById('navbarContent');
            if (navbar && navbar.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getOrCreateInstance(navbar);
                bsCollapse.hide();
            }
        }
    });
    
    // Add active state persistence
    const currentPath = window.location.pathname;
    const activeNavLinks = document.querySelectorAll('.nav-link');
    
    activeNavLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });
    
    console.log('🎨 Navbar Minimal Flat carregado com sucesso');
});
