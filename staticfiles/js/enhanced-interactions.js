/**
 * Lions CRM - Enhanced Interactions
 * Versão: 1.0.0 (23/05/2025)
 * Melhorias de interatividade para as ferramentas do CRM
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // SISTEMA DE NOTIFICAÇÕES TOAST
    // ========================================
    
    class ToastNotification {
        constructor() {
            this.createContainer();
        }
        
        createContainer() {
            if (!document.getElementById('toast-container')) {
                const container = document.createElement('div');
                container.id = 'toast-container';
                container.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                `;
                document.body.appendChild(container);
            }
        }
        
        show(message, type = 'info', duration = 4000) {
            const toast = document.createElement('div');
            const colors = {
                success: { bg: '#4caf50', border: '#45a049' },
                error: { bg: '#f44336', border: '#da190b' },
                warning: { bg: '#ff9800', border: '#f57f17' },
                info: { bg: '#2196f3', border: '#1976d2' }
            };
            
            const color = colors[type] || colors.info;
            
            toast.style.cssText = `
                background: ${color.bg};
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                border-left: 4px solid ${color.border};
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                font-weight: 500;
                max-width: 350px;
                animation: slideInRight 0.3s ease-out;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            `;
            
            toast.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px;">
                    <i class="bi bi-${this.getIcon(type)}"></i>
                    <span>${message}</span>
                    <i class="bi bi-x-lg" style="margin-left: auto; cursor: pointer; opacity: 0.7;"></i>
                </div>
            `;
            
            // Progress bar
            const progressBar = document.createElement('div');
            progressBar.style.cssText = `
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: rgba(255,255,255,0.8);
                width: 100%;
                animation: progressShrink ${duration}ms linear;
            `;
            toast.appendChild(progressBar);
            
            document.getElementById('toast-container').appendChild(toast);
            
            // Auto remove
            setTimeout(() => this.remove(toast), duration);
            
            // Click to remove
            toast.addEventListener('click', () => this.remove(toast));
        }
        
        getIcon(type) {
            const icons = {
                success: 'check-circle',
                error: 'exclamation-triangle',
                warning: 'exclamation-triangle',
                info: 'info-circle'
            };
            return icons[type] || icons.info;
        }
        
        remove(toast) {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }
    
    // CSS para animações dos toasts
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        @keyframes progressShrink {
            from { width: 100%; }
            to { width: 0%; }
        }
    `;
    document.head.appendChild(style);
    
    // Instância global do toast
    window.toast = new ToastNotification();
    
    // ========================================
    // SISTEMA DE CONFIRMAÇÃO PERSONALIZADO
    // ========================================
    
    class CustomConfirm {
        show(message, options = {}) {
            return new Promise((resolve) => {
                const modal = document.createElement('div');
                modal.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.7);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    animation: fadeIn 0.3s ease-out;
                `;
                
                const dialog = document.createElement('div');
                dialog.style.cssText = `
                    background: var(--color-dark-lighter);
                    border-radius: 12px;
                    padding: 2rem;
                    max-width: 400px;
                    width: 90%;
                    text-align: center;
                    border: 1px solid var(--color-gold);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    animation: scaleIn 0.3s ease-out;
                `;
                
                dialog.innerHTML = `
                    <div style="margin-bottom: 1.5rem;">
                        <i class="bi bi-question-circle" style="font-size: 3rem; color: var(--color-gold); margin-bottom: 1rem;"></i>
                        <h4 style="color: var(--color-text); margin-bottom: 0.5rem;">${options.title || 'Confirmação'}</h4>
                        <p style="color: var(--color-text-muted); margin: 0;">${message}</p>
                    </div>
                    <div style="display: flex; gap: 1rem; justify-content: center;">
                        <button id="confirm-cancel" class="btn btn-outline-secondary" style="min-width: 100px;">
                            ${options.cancelText || 'Cancelar'}
                        </button>
                        <button id="confirm-ok" class="btn btn-gold" style="min-width: 100px;">
                            ${options.confirmText || 'Confirmar'}
                        </button>
                    </div>
                `;
                
                modal.appendChild(dialog);
                document.body.appendChild(modal);
                
                // Event listeners
                document.getElementById('confirm-cancel').addEventListener('click', () => {
                    this.remove(modal);
                    resolve(false);
                });
                
                document.getElementById('confirm-ok').addEventListener('click', () => {
                    this.remove(modal);
                    resolve(true);
                });
                
                // Click fora para cancelar
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        this.remove(modal);
                        resolve(false);
                    }
                });
                
                // ESC para cancelar
                const escHandler = (e) => {
                    if (e.key === 'Escape') {
                        document.removeEventListener('keydown', escHandler);
                        this.remove(modal);
                        resolve(false);
                    }
                };
                document.addEventListener('keydown', escHandler);
            });
        }
        
        remove(modal) {
            modal.style.animation = 'fadeOut 0.3s ease-in';
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
            }, 300);
        }
    }
    
    // CSS para animações do modal
    const modalStyle = document.createElement('style');
    modalStyle.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        
        @keyframes scaleIn {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
    `;
    document.head.appendChild(modalStyle);
    
    // Instância global do confirm
    window.customConfirm = new CustomConfirm();
    
    // ========================================
    // MELHORIAS NOS FORMULÁRIOS
    // ========================================
    
    // Auto-focus no primeiro campo de formulários
    const firstInput = document.querySelector('.enhanced-form input:not([type="hidden"]), .enhanced-form select, .enhanced-form textarea');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Validação em tempo real melhorada
    function setupAdvancedValidation() {
        const inputs = document.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Feedback visual imediato
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.style.borderColor = '#4caf50';
                    this.style.boxShadow = '0 0 5px rgba(76, 175, 80, 0.3)';
                } else {
                    this.style.borderColor = '#f44336';
                    this.style.boxShadow = '0 0 5px rgba(244, 67, 54, 0.3)';
                }
            });
            
            input.addEventListener('focus', function() {
                this.style.borderColor = 'var(--color-gold)';
                this.style.boxShadow = '0 0 5px rgba(212, 175, 55, 0.3)';
            });
        });
    }
    
    setupAdvancedValidation();
    
    // ========================================
    // SISTEMA DE BUSCA INTELIGENTE
    // ========================================
    
    function setupSmartSearch() {
        const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="buscar"], input[placeholder*="pesquisar"]');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', function() {
                const query = this.value.trim();
                
                // Debounce para evitar muitas requisições
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    if (query.length >= 2) {
                        performSearch(query, this);
                    }
                }, 300);
            });
        });
    }
    
    function performSearch(query, inputElement) {
        // Implementar busca baseada no contexto
        console.log('Buscando:', query);
        // Aqui seria implementada a lógica de busca específica
    }
    
    setupSmartSearch();
    
    // ========================================
    // KEYBOARD SHORTCUTS
    // ========================================
    
    document.addEventListener('keydown', function(e) {
        // Ctrl + S para salvar formulários
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const submitButton = document.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton) {
                submitButton.click();
                toast.show('Formulário salvo!', 'success');
            }
        }
        
        // Ctrl + Enter para ações principais
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            const primaryButton = document.querySelector('.btn-gold, .btn-primary');
            if (primaryButton) {
                primaryButton.click();
            }
        }
        
        // ESC para fechar modais/dropdowns
        if (e.key === 'Escape') {
            const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
            openDropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
    
    // ========================================
    // MELHORIAS NO CALENDÁRIO
    // ========================================
    
    function setupCalendarEnhancements() {
        const calendarDays = document.querySelectorAll('.calendar-day');
        
        calendarDays.forEach(day => {
            day.addEventListener('click', function() {
                // Remover seleção anterior
                document.querySelectorAll('.calendar-day.selected').forEach(d => {
                    d.classList.remove('selected');
                });
                
                // Adicionar seleção atual
                this.classList.add('selected');
                
                // Feedback haptico (se suportado)
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
                
                // Carregar eventos do dia
                loadDayEvents(this.dataset.date);
            });
            
            // Hover effect melhorado
            day.addEventListener('mouseenter', function() {
                if (!this.classList.contains('selected')) {
                    this.style.transform = 'scale(1.1)';
                    this.style.zIndex = '10';
                }
            });
            
            day.addEventListener('mouseleave', function() {
                if (!this.classList.contains('selected')) {
                    this.style.transform = '';
                    this.style.zIndex = '';
                }
            });
        });
    }
    
    function loadDayEvents(date) {
        // Implementar carregamento de eventos
        console.log('Carregando eventos para:', date);
    }
    
    setupCalendarEnhancements();
    
    // ========================================
    // SISTEMA DE AJUDA CONTEXTUAL
    // ========================================
    
    function setupContextualHelp() {
        // Adicionar ícones de ajuda
        const helpElements = document.querySelectorAll('[data-help]');
        
        helpElements.forEach(element => {
            const helpIcon = document.createElement('i');
            helpIcon.className = 'bi bi-question-circle ms-1';
            helpIcon.style.cssText = `
                color: var(--color-gold);
                cursor: help;
                font-size: 0.9rem;
            `;
            
            helpIcon.title = element.dataset.help;
            element.appendChild(helpIcon);
        });
    }
    
    setupContextualHelp();
    
    // ========================================
    // AUTO-SAVE PARA FORMULÁRIOS
    // ========================================
    
    function setupAutoSave() {
        const forms = document.querySelectorAll('form[data-autosave]');
        
        forms.forEach(form => {
            const formId = form.dataset.autosave;
            
            // Restaurar dados salvos
            const savedData = localStorage.getItem(`autosave_${formId}`);
            if (savedData) {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(name => {
                    const field = form.querySelector(`[name="${name}"]`);
                    if (field) {
                        field.value = data[name];
                    }
                });
            }
            
            // Salvar automaticamente
            form.addEventListener('input', debounce(() => {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
            }, 1000));
        });
    }
    
    // Utility function para debounce
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
    
    setupAutoSave();
    
    // ========================================
    // MELHORIAS DE PERFORMANCE
    // ========================================
    
    // Lazy loading para imagens
    function setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }
    }
    
    setupLazyLoading();
    
    // Preload de páginas importantes
    function preloadImportantPages() {
        const importantLinks = document.querySelectorAll('a[data-preload]');
        
        importantLinks.forEach(link => {
            link.addEventListener('mouseenter', () => {
                const prefetch = document.createElement('link');
                prefetch.rel = 'prefetch';
                prefetch.href = link.href;
                document.head.appendChild(prefetch);
            });
        });
    }
    
    preloadImportantPages();
    
    // ========================================
    // FEEDBACK DE SUCESSO GLOBAL
    // ========================================
    
    // Interceptar envios de formulário para feedback
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.tagName === 'FORM') {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="loading-spinner"></span> Processando...';
                submitButton.disabled = true;
                
                // Restaurar após um tempo (caso não haja redirecionamento)
                setTimeout(() => {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 3000);
            }
        }
    });
    
    console.log('🚀 Lions CRM Enhanced Interactions carregado com sucesso!');
});
