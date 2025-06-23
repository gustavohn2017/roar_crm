/*
 * Notification System - Lions CRM
 * Sistema de notificações visuais e feedback para o usuário
 * Data: 23/05/2025
 */

class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
        this.notifications = [];
        this.maxNotifications = 5;
        this.defaultDuration = 5000;
    }

    createContainer() {
        let container = document.querySelector('.notification-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(type, title, message, duration = this.defaultDuration) {
        const notification = this.createNotification(type, title, message);
        
        // Limitar número de notificações
        if (this.notifications.length >= this.maxNotifications) {
            this.remove(this.notifications[0]);
        }

        this.container.appendChild(notification);
        this.notifications.push(notification);

        // Animação de entrada
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Auto-remover após duração especificada
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    createNotification(type, title, message) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: 'bi-check',
            warning: 'bi-exclamation-triangle',
            error: 'bi-x-circle',
            info: 'bi-info-circle'
        };

        notification.innerHTML = `
            <div class="notification-header">
                <div class="notification-icon">
                    <i class="${icons[type] || icons.info}"></i>
                </div>
                <h6 class="notification-title">${title}</h6>
                <button class="notification-close" type="button">
                    <i class="bi bi-x"></i>
                </button>
            </div>
            <div class="notification-content">${message}</div>
            <div class="notification-progress"></div>
        `;

        // Adicionar evento de fechamento
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.remove(notification);
        });

        return notification;
    }

    remove(notification) {
        if (notification && notification.parentNode) {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                
                const index = this.notifications.indexOf(notification);
                if (index > -1) {
                    this.notifications.splice(index, 1);
                }
            }, 300);
        }
    }

    success(title, message, duration) {
        return this.show('success', title, message, duration);
    }

    warning(title, message, duration) {
        return this.show('warning', title, message, duration);
    }

    error(title, message, duration) {
        return this.show('error', title, message, duration);
    }

    info(title, message, duration) {
        return this.show('info', title, message, duration);
    }

    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
    }
}

// Criar instância global
window.notifications = new NotificationSystem();

/*
 * Enhanced Calculator Manager
 * Gerenciador avançado para as calculadoras com validações e feedback
 */

class EnhancedCalculatorManager {
    constructor() {
        this.currentCalculation = null;
        this.validationRules = {};
        this.init();
    }

    init() {
        this.setupValidationRules();
        this.enhanceCalculatorForms();
        this.setupCalculationHistory();
        this.setupKeyboardNavigation();
        this.setupProgressIndicators();
    }

    setupValidationRules() {
        this.validationRules = {
            'carValue': {
                min: 10000,
                max: 500000,
                message: 'Valor deve estar entre R$ 10.000 e R$ 500.000'
            },
            'propertyValue': {
                min: 50000,
                max: 2000000,
                message: 'Valor deve estar entre R$ 50.000 e R$ 2.000.000'
            },
            'carRate': {
                min: 10,
                max: 25,
                message: 'Taxa deve estar entre 10% e 25%'
            },
            'propertyRate': {
                min: 8,
                max: 20,
                message: 'Taxa deve estar entre 8% e 20%'
            }
        };
    }

    enhanceCalculatorForms() {
        const forms = document.querySelectorAll('.calculator-form');
        
        forms.forEach(form => {
            this.addFormEnhancements(form);
            this.setupRealTimeCalculation(form);
            this.addFormValidation(form);
        });
    }

    addFormEnhancements(form) {
        // Adicionar indicadores de progresso
        const progressDiv = document.createElement('div');
        progressDiv.className = 'progress-indicator';
        progressDiv.innerHTML = `
            <div class="progress-step active">
                <div class="progress-step-circle">1</div>
                <div class="progress-step-label">Dados</div>
            </div>
            <div class="progress-step">
                <div class="progress-step-circle">2</div>
                <div class="progress-step-label">Cálculo</div>
            </div>
            <div class="progress-step">
                <div class="progress-step-circle">3</div>
                <div class="progress-step-label">Resultado</div>
            </div>
        `;
        
        form.insertBefore(progressDiv, form.firstChild);

        // Adicionar labels de campo obrigatório
        const requiredFields = form.querySelectorAll('input[required], select[required]');
        requiredFields.forEach(field => {
            const label = form.querySelector(`label[for="${field.id}"]`);
            if (label) {
                label.classList.add('required');
            }
        });
    }

    setupRealTimeCalculation(form) {
        const inputs = form.querySelectorAll('input, select');
        let debounceTimer;

        inputs.forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.performCalculation(form);
                }, 500);
            });
        });
    }

    addFormValidation(form) {
        const submitBtn = form.querySelector('.calculator-btn');
        
        if (submitBtn) {
            submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                
                if (this.validateForm(form)) {
                    this.performCalculation(form);
                    this.updateProgressStep(form, 2);
                    
                    setTimeout(() => {
                        this.updateProgressStep(form, 3);
                        notifications.success(
                            'Cálculo Realizado!',
                            'Simulação calculada com sucesso. Você pode gerar a proposta em PDF.'
                        );
                    }, 1000);
                } else {
                    notifications.error(
                        'Erro na Validação',
                        'Por favor, corrija os campos com erro antes de continuar.'
                    );
                }
            });
        }
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[type="number"], input[type="range"]');

        inputs.forEach(input => {
            const fieldName = input.id;
            const value = parseFloat(input.value);
            const rules = this.validationRules[fieldName];

            if (rules) {
                if (value < rules.min || value > rules.max) {
                    this.showFieldError(input, rules.message);
                    isValid = false;
                } else {
                    this.clearFieldError(input);
                }
            }
        });

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid', 'error');
        
        let errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        
        // Efeito de shake
        setTimeout(() => {
            field.classList.remove('error');
        }, 500);
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    performCalculation(form) {
        // Adicionar estado de loading
        form.classList.add('loading');
        
        setTimeout(() => {
            form.classList.remove('loading');
            
            // Detectar tipo de calculadora e executar cálculo apropriado
            if (form.id === 'carConsortiumForm') {
                this.calculateCarConsortium();
            } else if (form.id === 'propertyConsortiumForm') {
                this.calculatePropertyConsortium();
            }
        }, 800);
    }

    calculateCarConsortium() {
        // Implementar cálculo do consórcio de carros
        const carValue = parseFloat(document.getElementById('carValue').value);
        const planDuration = parseInt(document.getElementById('carPlanDuration').value);
        const adminRate = parseFloat(document.getElementById('carRate').value) / 100;
        const fundFee = parseFloat(document.getElementById('carFundFee').value) / 100;
        const entryFee = parseFloat(document.getElementById('carEntryFee').value) / 100;
        
        const adminFeeTotal = carValue * adminRate;
        const fundFeeTotal = carValue * fundFee;
        const entryFeeTotal = carValue * entryFee;
        const totalPlanValue = carValue + adminFeeTotal + fundFeeTotal + entryFeeTotal;
        const monthlyPayment = totalPlanValue / planDuration;
        
        this.updateCarResults({
            carValue,
            monthlyPayment,
            adminFeeTotal,
            fundFeeTotal,
            entryFeeTotal,
            totalPlanValue,
            planDuration,
            adminRate
        });

        // Salvar no histórico
        this.saveCalculationHistory('Consórcio Auto', {
            value: carValue,
            monthlyPayment: monthlyPayment,
            duration: planDuration,
            type: 'auto'
        });
    }

    calculatePropertyConsortium() {
        // Implementar cálculo do consórcio imobiliário
        const propertyValue = parseFloat(document.getElementById('propertyValue').value);
        const planDuration = parseInt(document.getElementById('propertyPlanDuration').value);
        const adminRate = parseFloat(document.getElementById('propertyRate').value) / 100;
        
        const adminFeeTotal = propertyValue * adminRate;
        const totalPlanValue = propertyValue + adminFeeTotal;
        const monthlyPayment = totalPlanValue / planDuration;
        
        this.updatePropertyResults({
            propertyValue,
            monthlyPayment,
            adminFeeTotal,
            totalPlanValue,
            planDuration,
            adminRate
        });

        // Salvar no histórico
        this.saveCalculationHistory('Consórcio Imóvel', {
            value: propertyValue,
            monthlyPayment: monthlyPayment,
            duration: planDuration,
            type: 'property'
        });
    }

    updateCarResults(data) {
        const formatter = new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });

        // Atualizar com animação
        this.animateValueUpdate('carMonthlyPayment', data.monthlyPayment, formatter);
        this.animateValueUpdate('carTotalCredit', data.carValue, formatter);
        
        document.getElementById('carTotalAdminFee').textContent = 
            `${formatter.format(data.adminFeeTotal)} (${(data.adminRate * 100).toFixed(1)}%)`;
        document.getElementById('carTotalFundFee').textContent = 
            `${formatter.format(data.fundFeeTotal)}`;
        document.getElementById('carTotalEntryFee').textContent = 
            `${formatter.format(data.entryFeeTotal)}`;
        
        this.animateValueUpdate('carTotalPlanValue', data.totalPlanValue, formatter);
        
        const years = Math.floor(data.planDuration / 12);
        const remainingMonths = data.planDuration % 12;
        document.getElementById('carPlanDurationResult').textContent = 
            `${data.planDuration} meses (${years} anos${remainingMonths ? ' e ' + remainingMonths + ' meses' : ''})`;
    }

    updatePropertyResults(data) {
        const formatter = new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });

        this.animateValueUpdate('propertyMonthlyPayment', data.monthlyPayment, formatter);
        this.animateValueUpdate('propertyTotalCredit', data.propertyValue, formatter);
        
        document.getElementById('propertyTotalAdminFee').textContent = 
            `${formatter.format(data.adminFeeTotal)} (${(data.adminRate * 100).toFixed(1)}%)`;
        
        this.animateValueUpdate('propertyTotalPlanValue', data.totalPlanValue, formatter);
        
        const years = Math.floor(data.planDuration / 12);
        const remainingMonths = data.planDuration % 12;
        document.getElementById('propertyPlanDurationResult').textContent = 
            `${data.planDuration} meses (${years} anos${remainingMonths ? ' e ' + remainingMonths + ' meses' : ''})`;
    }

    animateValueUpdate(elementId, targetValue, formatter) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const currentValue = this.parseValueFromElement(element);
        const increment = (targetValue - currentValue) / 30;
        let currentStep = currentValue;
        
        const animation = setInterval(() => {
            currentStep += increment;
            
            if ((increment > 0 && currentStep >= targetValue) || 
                (increment < 0 && currentStep <= targetValue)) {
                currentStep = targetValue;
                clearInterval(animation);
            }
            
            element.textContent = formatter.format(currentStep);
        }, 16);
    }

    parseValueFromElement(element) {
        const text = element.textContent.replace(/[^\d,.-]/g, '').replace(',', '.');
        return parseFloat(text) || 0;
    }

    updateProgressStep(form, step) {
        const progressSteps = form.querySelectorAll('.progress-step');
        
        progressSteps.forEach((stepElement, index) => {
            if (index < step) {
                stepElement.classList.add('completed');
                stepElement.classList.remove('active');
            } else if (index === step - 1) {
                stepElement.classList.add('active');
                stepElement.classList.remove('completed');
            } else {
                stepElement.classList.remove('active', 'completed');
            }
        });
    }

    setupCalculationHistory() {
        this.calculationHistory = JSON.parse(localStorage.getItem('calculationHistory') || '[]');
    }

    saveCalculationHistory(type, data) {
        const entry = {
            id: Date.now(),
            type,
            data,
            timestamp: new Date().toISOString(),
            date: new Date().toLocaleDateString('pt-BR')
        };

        this.calculationHistory.unshift(entry);
        
        // Manter apenas os últimos 20 cálculos
        if (this.calculationHistory.length > 20) {
            this.calculationHistory = this.calculationHistory.slice(0, 20);
        }

        localStorage.setItem('calculationHistory', JSON.stringify(this.calculationHistory));
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // F5 para recalcular
            if (e.key === 'F5') {
                e.preventDefault();
                const activeForm = document.querySelector('.tab-pane.active .calculator-form');
                if (activeForm) {
                    this.performCalculation(activeForm);
                }
            }

            // Escape para limpar notificações
            if (e.key === 'Escape') {
                notifications.clear();
            }
        });
    }

    setupProgressIndicators() {
        // Configurar indicadores de progresso para acompanhar o preenchimento do formulário
        const forms = document.querySelectorAll('.calculator-form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select');
            
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    this.updateFormProgress(form);
                });
            });
        });
    }

    updateFormProgress(form) {
        const inputs = form.querySelectorAll('input[required], select[required]');
        const filledInputs = Array.from(inputs).filter(input => input.value.trim() !== '');
        const progress = (filledInputs.length / inputs.length) * 100;
        
        // Atualizar indicador de progresso se existir
        const progressBar = form.querySelector('.form-progress');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        // Atualizar step se todos os campos estão preenchidos
        if (progress === 100) {
            this.updateProgressStep(form, 2);
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new EnhancedCalculatorManager();
    
    // Mostrar notificação de boas-vindas
    setTimeout(() => {
        notifications.info(
            'Calculadoras Carregadas!',
            'Use as abas para alternar entre diferentes tipos de consórcio. Pressione Ctrl+Enter para calcular rapidamente.',
            7000
        );
    }, 1000);
});
