/*
 * Calculator Enhancements - Lions CRM
 * Melhorias de UX e funcionalidades avançadas para as calculadoras
 * Data: 23/05/2025
 */

class CalculatorEnhancements {
    constructor() {
        this.initialized = false;
        this.init();
    }

    init() {
        if (this.initialized) return;
        
        this.setupAnimations();
        this.setupTooltips();
        this.setupKeyboardShortcuts();
        this.setupResultsComparison();
        this.setupAdvancedValidation();
        this.setupAutoSave();
        this.setupThemeToggle();
        this.setupPrintFriendly();
        
        this.initialized = true;
        console.log('Calculator Enhancements initialized');
    }

    // =====================================
    // ANIMAÇÕES E TRANSIÇÕES SUAVES
    // =====================================
    
    setupAnimations() {
        // Animação de entrada para cartões
        const cards = document.querySelectorAll('.calculator-card, .result-card');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'slideInUp 0.6s ease-out forwards';
                }
            });
        }, { threshold: 0.1 });

        cards.forEach(card => observer.observe(card));

        // Efeito de digitação nos valores
        this.setupCounterAnimations();
        
        // Animação de progresso nos sliders
        this.setupSliderAnimations();
    }

    setupCounterAnimations() {
        const animateCounter = (element, start, end, duration = 1000) => {
            const increment = (end - start) / (duration / 16);
            let current = start;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= end) {
                    current = end;
                    clearInterval(timer);
                }
                
                const formatter = new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                });
                
                element.textContent = formatter.format(current);
            }, 16);
        };

        window.animateValue = animateCounter;
    }

    setupSliderAnimations() {
        const sliders = document.querySelectorAll('.form-range');
        
        sliders.forEach(slider => {
            slider.addEventListener('input', (e) => {
                const percent = (e.target.value - e.target.min) / (e.target.max - e.target.min) * 100;
                
                // Criar gradiente dinâmico baseado no valor
                const gradient = `linear-gradient(90deg, 
                    var(--color-gold) 0%, 
                    var(--color-gold) ${percent}%, 
                    var(--color-dark-light) ${percent}%, 
                    var(--color-dark-light) 100%)`;
                
                e.target.style.background = gradient;
                
                // Adicionar efeito de pulso no thumb
                e.target.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    e.target.style.transform = 'scale(1)';
                }, 150);
            });
        });
    }

    // =====================================
    // TOOLTIPS INFORMATIVOS AVANÇADOS
    // =====================================
    
    setupTooltips() {
        const tooltipData = {
            'carRate': {
                title: 'Taxa de Administração',
                content: 'Percentual cobrado mensalmente pela administradora para gerenciar o grupo de consórcio. Varia entre 10% e 20% do valor da carta.',
                icon: 'bi-info-circle'
            },
            'carEntryFee': {
                title: 'Taxa de Adesão',
                content: 'Taxa única paga no momento da adesão ao consórcio. Cobre custos administrativos iniciais.',
                icon: 'bi-door-open'
            },
            'carFundFee': {
                title: 'Fundo de Reserva',
                content: 'Percentual destinado ao fundo de reserva para cobrir eventuais inadimplências do grupo.',
                icon: 'bi-shield-check'
            },
            'carPlanDuration': {
                title: 'Prazo do Plano',
                content: 'Duração total do consórcio em meses. Prazos mais longos resultam em parcelas menores.',
                icon: 'bi-calendar-range'
            }
        };

        Object.keys(tooltipData).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                this.createTooltip(element, tooltipData[id]);
            }
        });
    }

    createTooltip(element, data) {
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-header">
                <i class="${data.icon}"></i>
                <strong>${data.title}</strong>
            </div>
            <div class="tooltip-content">${data.content}</div>
        `;
        
        document.body.appendChild(tooltip);

        element.addEventListener('mouseenter', (e) => {
            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.opacity = '1';
            tooltip.style.visibility = 'visible';
        });

        element.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
            tooltip.style.visibility = 'hidden';
        });
    }

    // =====================================
    // ATALHOS DE TECLADO
    // =====================================
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl + Enter para calcular
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                const activeTab = document.querySelector('.nav-link.active');
                if (activeTab) {
                    const calculateBtn = document.querySelector(`#${activeTab.id.replace('-tab', '')}-calculator .calculator-btn`);
                    if (calculateBtn) calculateBtn.click();
                }
            }

            // Ctrl + P para gerar PDF
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                const generateBtn = document.querySelector('.btn-outline-gold');
                if (generateBtn) generateBtn.click();
            }

            // Tab + Tab para alternar calculadoras
            if (e.key === 'Tab' && e.shiftKey && e.ctrlKey) {
                e.preventDefault();
                this.switchCalculatorTab();
            }
        });
    }

    switchCalculatorTab() {
        const tabs = document.querySelectorAll('.calculator-tabs .nav-link');
        const activeTab = document.querySelector('.calculator-tabs .nav-link.active');
        const currentIndex = Array.from(tabs).indexOf(activeTab);
        const nextIndex = (currentIndex + 1) % tabs.length;
        
        tabs[nextIndex].click();
    }

    // =====================================
    // COMPARAÇÃO DE RESULTADOS
    // =====================================
    
    setupResultsComparison() {
        this.resultsHistory = JSON.parse(localStorage.getItem('calculatorHistory') || '[]');
        this.createComparisonPanel();
    }

    createComparisonPanel() {
        const comparisonButton = document.createElement('button');
        comparisonButton.className = 'btn btn-outline-secondary position-fixed';
        comparisonButton.style.cssText = `
            bottom: 20px; 
            right: 20px; 
            z-index: 1000;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        comparisonButton.innerHTML = '<i class="bi bi-bar-chart"></i>';
        comparisonButton.title = 'Comparar Resultados';
        
        comparisonButton.addEventListener('click', () => {
            this.showComparisonModal();
        });

        document.body.appendChild(comparisonButton);
    }

    showComparisonModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content bg-dark">
                    <div class="modal-header">
                        <h5 class="modal-title text-gold">
                            <i class="bi bi-bar-chart"></i> Comparação de Resultados
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${this.generateComparisonContent()}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        new bootstrap.Modal(modal).show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    generateComparisonContent() {
        if (this.resultsHistory.length === 0) {
            return '<p class="text-center text-muted">Nenhuma simulação salva para comparar.</p>';
        }

        let content = '<div class="row">';
        this.resultsHistory.slice(-3).forEach((result, index) => {
            content += `
                <div class="col-md-4">
                    <div class="card bg-secondary mb-3">
                        <div class="card-header">
                            <h6>${result.type} - ${result.date}</h6>
                        </div>
                        <div class="card-body">
                            <p><strong>Valor:</strong> ${result.value}</p>
                            <p><strong>Parcela:</strong> ${result.monthlyPayment}</p>
                            <p><strong>Prazo:</strong> ${result.duration} meses</p>
                        </div>
                    </div>
                </div>
            `;
        });
        content += '</div>';

        return content;
    }

    saveResult(type, data) {
        const result = {
            type,
            date: new Date().toLocaleDateString('pt-BR'),
            timestamp: Date.now(),
            ...data
        };

        this.resultsHistory.push(result);
        
        // Manter apenas os últimos 10 resultados
        if (this.resultsHistory.length > 10) {
            this.resultsHistory = this.resultsHistory.slice(-10);
        }

        localStorage.setItem('calculatorHistory', JSON.stringify(this.resultsHistory));
    }

    // =====================================
    // VALIDAÇÃO AVANÇADA
    // =====================================
    
    setupAdvancedValidation() {
        const forms = document.querySelectorAll('.calculator-form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select');
            
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
                
                input.addEventListener('input', () => {
                    this.clearValidationError(input);
                });
            });
        });
    }

    validateField(field) {
        const value = parseFloat(field.value);
        const min = parseFloat(field.getAttribute('min'));
        const max = parseFloat(field.getAttribute('max'));
        let isValid = true;
        let message = '';

        if (field.type === 'number') {
            if (isNaN(value)) {
                isValid = false;
                message = 'Digite um valor numérico válido';
            } else if (min && value < min) {
                isValid = false;
                message = `Valor mínimo: ${min.toLocaleString('pt-BR')}`;
            } else if (max && value > max) {
                isValid = false;
                message = `Valor máximo: ${max.toLocaleString('pt-BR')}`;
            }
        }

        if (!isValid) {
            this.showFieldError(field, message);
        } else {
            this.clearValidationError(field);
        }

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
    }

    clearValidationError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // =====================================
    // AUTO-SAVE E RECUPERAÇÃO
    // =====================================
    
    setupAutoSave() {
        const forms = document.querySelectorAll('.calculator-form');
        
        forms.forEach((form, index) => {
            const inputs = form.querySelectorAll('input, select');
            
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.autoSaveFormData(form, index);
                });
            });
            
            // Restaurar dados salvos
            this.restoreFormData(form, index);
        });
    }

    autoSaveFormData(form, formIndex) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        localStorage.setItem(`calculator_form_${formIndex}`, JSON.stringify(data));
    }

    restoreFormData(form, formIndex) {
        const savedData = localStorage.getItem(`calculator_form_${formIndex}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"], #${key}`);
                if (field && field.value !== data[key]) {
                    field.value = data[key];
                    field.dispatchEvent(new Event('input'));
                }
            });
        }
    }

    // =====================================
    // TEMA ESCURO/CLARO
    // =====================================
    
    setupThemeToggle() {
        const themeToggle = document.createElement('button');
        themeToggle.className = 'btn btn-outline-secondary position-fixed';
        themeToggle.style.cssText = `
            top: 20px; 
            right: 20px; 
            z-index: 1000;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        this.updateThemeIcon(themeToggle);
        
        themeToggle.addEventListener('click', () => {
            this.toggleTheme();
            this.updateThemeIcon(themeToggle);
        });

        document.body.appendChild(themeToggle);
    }

    toggleTheme() {
        const currentTheme = localStorage.getItem('calculator_theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('calculator_theme', newTheme);
    }

    updateThemeIcon(button) {
        const currentTheme = localStorage.getItem('calculator_theme') || 'dark';
        button.innerHTML = currentTheme === 'dark' ? 
            '<i class="bi bi-sun"></i>' : 
            '<i class="bi bi-moon"></i>';
        button.title = currentTheme === 'dark' ? 'Tema Claro' : 'Tema Escuro';
    }

    // =====================================
    // VERSÃO PARA IMPRESSÃO
    // =====================================
    
    setupPrintFriendly() {
        const printButton = document.createElement('button');
        printButton.className = 'btn btn-outline-info ms-2';
        printButton.innerHTML = '<i class="bi bi-printer"></i> Imprimir';
        
        printButton.addEventListener('click', () => {
            this.generatePrintView();
        });

        // Adicionar ao header das calculadoras
        const header = document.querySelector('.calculator-header .d-flex > div:last-child');
        if (header) {
            header.appendChild(printButton);
        }
    }

    generatePrintView() {
        const printWindow = window.open('', '_blank');
        const content = this.generatePrintContent();
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Simulação de Consórcio - Lions CRM</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 20px;
                        color: #333;
                    }
                    .header { 
                        text-align: center; 
                        margin-bottom: 30px; 
                        border-bottom: 2px solid #d4af37;
                        padding-bottom: 20px;
                    }
                    .result-section { 
                        margin: 20px 0; 
                        padding: 15px;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                    }
                    .result-item { 
                        display: flex; 
                        justify-content: space-between; 
                        margin: 10px 0;
                        padding: 5px 0;
                        border-bottom: 1px solid #eee;
                    }
                    .highlight { 
                        font-weight: bold; 
                        color: #d4af37; 
                        font-size: 1.2em;
                    }
                </style>
            </head>
            <body>
                ${content}
            </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 250);
    }

    generatePrintContent() {
        const activeTab = document.querySelector('.tab-pane.active');
        const resultCards = activeTab ? activeTab.querySelectorAll('.result-card') : [];
        
        let content = `
            <div class="header">
                <h1>Simulação de Consórcio</h1>
                <p>Lions CRM - ${new Date().toLocaleDateString('pt-BR')}</p>
            </div>
        `;

        resultCards.forEach(card => {
            const results = card.querySelectorAll('.result-row, .result-item');
            content += '<div class="result-section">';
            
            results.forEach(result => {
                const label = result.querySelector('.result-label')?.textContent || '';
                const value = result.querySelector('span:last-child')?.textContent || '';
                if (label && value) {
                    content += `<div class="result-item"><span>${label}</span><span>${value}</span></div>`;
                }
            });
            
            content += '</div>';
        });

        return content;
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new CalculatorEnhancements();
});

// CSS adicional para tooltips personalizados
const tooltipStyles = `
    <style>
        .custom-tooltip {
            position: absolute;
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            color: #fff;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            max-width: 300px;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            border: 2px solid rgba(212, 175, 55, 0.3);
            backdrop-filter: blur(10px);
        }
        
        .tooltip-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
            color: #d4af37;
            font-weight: 700;
        }
        
        .tooltip-content {
            color: #ccc;
            line-height: 1.5;
            font-size: 14px;
        }
        
        [data-theme="light"] .calculator-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            color: #212529;
        }
        
        [data-theme="light"] .calculator-header {
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        }
        
        [data-theme="light"] .nav-tabs.calculator-tabs {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        .is-invalid {
            border-color: #dc3545 !important;
            box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
        }
        
        .invalid-feedback {
            display: block;
            width: 100%;
            margin-top: 0.25rem;
            font-size: 0.875em;
            color: #dc3545;
        }
    </style>
`;

document.head.insertAdjacentHTML('beforeend', tooltipStyles);
