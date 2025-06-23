/**
 * Roar CRM - Main JavaScript File
 * Versão: 3.0.0 (Consolidated)
 *
 * This file unifies all essential functionalities of the application:
 * 1. Core Initializations (Bootstrap components)
 * 2. Advanced UI/UX (Toast Notifications, Custom Modals, etc.)
 * 3. Responsive Handling
 * 4. Form Utilities (Masks, Validation, Auto-submit, CEP lookup)
 * 5. Specific component logic (e.g., Quick Lead Form)
 */

document.addEventListener('DOMContentLoaded', function() {

    // ========================================
    // 1. CORE & UI INITIALIZATIONS
    // ========================================

    // Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // --- Toast Notification System ---
    const Toast = {
        createContainer: function() {
            if (document.getElementById('toast-container')) return;
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;`;
            document.body.appendChild(container);
        },
        show: function(message, type = 'info', duration = 4000) {
            this.createContainer();
            const toast = document.createElement('div');
            const icons = { success: 'check-circle', error: 'exclamation-triangle', warning: 'exclamation-triangle', info: 'info-circle' };
            toast.className = `toast-notification toast-${type}`;
            toast.innerHTML = `
                <div class="toast-icon"><i class="bi bi-${icons[type] || icons.info}"></i></div>
                <div class="toast-message">${message}</div>
                <div class="toast-close"><i class="bi bi-x-lg"></i></div>
                <div class="toast-progress" style="animation-duration: ${duration}ms"></div>
            `;
            document.getElementById('toast-container').appendChild(toast);
            toast.querySelector('.toast-close').addEventListener('click', () => this.remove(toast));
            setTimeout(() => this.remove(toast), duration);
        },
        remove: function(toast) {
            toast.classList.add('fade-out');
            toast.addEventListener('animationend', () => toast.remove());
        }
    };
    window.showNotification = (message, type) => Toast.show(message, type);


    // ========================================
    // 2. RESPONSIVE HANDLER
    // ========================================
    const ResponsiveHandler = {
        adjust: function() {
            const isMobile = window.innerWidth < 768;
            document.body.classList.toggle('is-mobile', isMobile);
            document.body.classList.toggle('is-desktop', !isMobile);

            // Make tables responsive
            document.querySelectorAll('table:not(.no-responsive)').forEach(table => {
                if (!table.parentElement.classList.contains('table-responsive')) {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'table-responsive';
                    table.parentNode.insertBefore(wrapper, table);
                    wrapper.appendChild(table);
                }
            });
        }
    };
    ResponsiveHandler.adjust();
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => ResponsiveHandler.adjust(), 150);
    });


    // ========================================
    // 3. FORM UTILITIES
    // ========================================
    const FormUtils = {
        applyPhoneMask: function(input) {
            let value = input.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            if (value.length > 10) {
                value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
            } else if (value.length > 2) {
                 value = value.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
            } else if (value.length > 0) {
                value = value.replace(/^(\d*)/, '($1');
            }
            input.value = value;
        },
        applyMoneyMask: function(input) {
            let value = input.value.replace(/\D/g, '');
            if (value) {
                value = (parseInt(value, 10) / 100).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            } else {
                value = '';
            }
            input.value = value;
        },
        initializeValidation: function() {
            const forms = document.querySelectorAll('.needs-validation');
            forms.forEach(form => {
                form.addEventListener('submit', event => {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                }, false);
            });
        },
        setupModalFocus: function() {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.addEventListener('shown.bs.modal', () => {
                    const firstInput = modal.querySelector('input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled])');
                    if (firstInput) firstInput.focus();
                });
            });
        },
        handleCepLookup: async function(cepField) {
            const cep = cepField.value.replace(/\D/g, '');
            if (cep.length !== 8) return;
            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                const data = await response.json();
                if (!data.erro) {
                    document.getElementById('id_logradouro').value = data.logradouro;
                    document.getElementById('id_bairro').value = data.bairro;
                    document.getElementById('id_cidade').value = data.localidade;
                    document.getElementById('id_estado').value = data.uf;
                    document.getElementById('id_numero').focus();
                }
            } catch (error) {
                console.error('Erro ao buscar CEP:', error);
            }
        }
    };

    // Apply listeners for FormUtils
    document.querySelectorAll('.phone-mask').forEach(input => input.addEventListener('input', () => FormUtils.applyPhoneMask(input)));
    document.querySelectorAll('.money-mask').forEach(input => input.addEventListener('input', () => FormUtils.applyMoneyMask(input)));
    const cepField = document.getElementById('id_cep');
    if (cepField) cepField.addEventListener('blur', () => FormUtils.handleCepLookup(cepField));
    FormUtils.initializeValidation();
    FormUtils.setupModalFocus();


    // ========================================
    // 4. SPECIFIC COMPONENT LOGIC
    // ========================================

    // --- Quick Lead Form ---
    const quickLeadModal = document.getElementById('quickLeadModal');
    if (quickLeadModal) {
        // Reset form on close
        quickLeadModal.addEventListener('hidden.bs.modal', function () {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            }
        });

        // WhatsApp checkbox logic
        const whatsappCheckbox = document.getElementById('id_is_whatsapp');
        const telefoneInput = document.getElementById('id_telefone');
        const whatsappInput = document.getElementById('id_whatsapp');
        if (whatsappCheckbox && telefoneInput && whatsappInput) {
            whatsappCheckbox.addEventListener('change', function() {
                whatsappInput.value = this.checked ? telefoneInput.value : '';
            });
            telefoneInput.addEventListener('input', function() {
                if (whatsappCheckbox.checked) {
                    whatsappInput.value = this.value;
                }
            });
        }
    }

    console.log('🚀 Roar CRM Main Script (v3.0) loaded successfully!');
});
