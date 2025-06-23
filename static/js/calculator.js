/**
 * Lions CRM - Unified Calculator Script
 * Version: 3.0.0 (24/05/2025)
 * 
 * This script combines the functionality from the following files:
 * - calculadora-consorcios.js (Core logic, State saving)
 * - calculator-notifications.js (Notifications, Enhanced Management, Validation)
 * - calculator-enhancements.js (UX/UI improvements, Animations, Shortcuts)
 * - advanced-calculator.js (Advanced features like Comparison, Recommendations)
 * 
 * The code has been refactored to eliminate redundancy and improve maintainability.
 */

document.addEventListener('DOMContentLoaded', function() {

    // =======================================
    // SECTION 1: CORE SYSTEMS & UTILITIES
    // =======================================

    /**
     * Notification System
     * Creates and manages toast-style notifications.
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
            if (this.notifications.length >= this.maxNotifications) {
                this.remove(this.notifications[0]);
            }
            this.container.appendChild(notification);
            this.notifications.push(notification);
            requestAnimationFrame(() => {
                notification.classList.add('show');
            });
            if (duration > 0) {
                setTimeout(() => this.remove(notification), duration);
            }
            return notification;
        }

        createNotification(type, title, message) {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            const icons = {
                success: 'bi-check-circle-fill',
                warning: 'bi-exclamation-triangle-fill',
                error: 'bi-x-circle-fill',
                info: 'bi-info-circle-fill'
            };
            notification.innerHTML = `
                <div class="notification-header">
                    <div class="notification-icon"><i class="bi ${icons[type] || icons.info}"></i></div>
                    <h6 class="notification-title">${title}</h6>
                    <button class="notification-close" type="button"><i class="bi bi-x"></i></button>
                </div>
                <div class="notification-content">${message}</div>
                <div class="notification-progress" style="animation-duration: ${this.defaultDuration}ms"></div>
            `;
            notification.querySelector('.notification-close').addEventListener('click', () => this.remove(notification));
            return notification;
        }

        remove(notification) {
            if (notification && notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                    const index = this.notifications.indexOf(notification);
                    if (index > -1) this.notifications.splice(index, 1);
                }, 300);
            }
        }

        success(title, message, duration) { return this.show('success', title, message, duration); }
        warning(title, message, duration) { return this.show('warning', title, message, duration); }
        error(title, message, duration) { return this.show('error', title, message, duration); }
        info(title, message, duration) { return this.show('info', title, message, duration); }
    }
    window.notifications = new NotificationSystem();

    /**
     * Currency Formatter
     */
    const formatter = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2
    });

    // =======================================
    // SECTION 2: ADVANCED FEATURE MODULES
    // (From advanced-calculator.js)
    // =======================================

    class ConsortiumComparator {
        constructor() {
            this.plans = [];
            this.createComparisonInterface();
        }
        createComparisonInterface() {
            const comparisonTab = document.querySelector('#comparison-calculator');
            if (!comparisonTab) return;
            comparisonTab.innerHTML = `
                <div class="row"><div class="col-12"><div class="tool-card"><div class="tool-card-header"><h5 class="tool-card-title"><span class="tool-card-icon"><i class="bi bi-bar-chart"></i></span> Comparativo de Planos</h5></div><div class="tool-card-body"><div class="comparison-controls mb-4"><div class="row"><div class="col-md-4"><label class="form-label">Tipo de Consórcio</label><select id="comparisonType" class="form-select"><option value="auto">Automóvel</option><option value="property">Imóvel</option></select></div><div class="col-md-4"><label class="form-label">Valor do Crédito</label><input type="number" id="comparisonValue" class="form-control" value="100000" min="10000"></div><div class="col-md-4"><button id="addPlanBtn" class="btn btn-gold mt-4"><i class="bi bi-plus"></i> Adicionar Plano</button></div></div></div><div id="comparisonResults" class="comparison-results"></div></div></div></div></div>`;
            this.bindEvents();
        }
        bindEvents() {
            document.getElementById('addPlanBtn')?.addEventListener('click', () => this.addPlan());
        }
        addPlan() {
            const value = parseFloat(document.getElementById('comparisonValue').value);
            const planVariations = [
                { duration: 36, adminRate: 0.18, fundFee: 0.02 },
                { duration: 48, adminRate: 0.16, fundFee: 0.015 },
                { duration: 60, adminRate: 0.165, fundFee: 0.015 },
                { duration: 72, adminRate: 0.15, fundFee: 0.01 },
                { duration: 84, adminRate: 0.145, fundFee: 0.01 }
            ];
            this.plans = planVariations.map((plan, index) => {
                const adminFeeTotal = value * plan.adminRate;
                const fundFeeTotal = value * plan.fundFee;
                const totalPlanValue = value + adminFeeTotal + fundFeeTotal;
                const monthlyPayment = totalPlanValue / plan.duration;
                return { id: index + 1, name: `Plano ${plan.duration} meses`, duration: plan.duration, adminRate: plan.adminRate, monthlyPayment, totalPlanValue, creditValue: value };
            });
            this.renderComparison();
        }
        renderComparison() {
            const container = document.getElementById('comparisonResults');
            if (!container) return;
            const bestMonthly = this.plans.reduce((prev, curr) => prev.monthlyPayment < curr.monthlyPayment ? prev : curr);
            const bestTotal = this.plans.reduce((prev, curr) => prev.totalPlanValue < curr.totalPlanValue ? prev : curr);
            container.innerHTML = `
                <div class="comparison-header mb-4"><h6 class="text-gold">Comparação de ${this.plans.length} Planos</h6><div class="comparison-summary"><div class="summary-item"><i class="bi bi-trophy text-success"></i><span>Menor Parcela: ${formatter.format(bestMonthly.monthlyPayment)} (${bestMonthly.name})</span></div><div class="summary-item"><i class="bi bi-star text-warning"></i><span>Menor Total: ${formatter.format(bestTotal.totalPlanValue)} (${bestTotal.name})</span></div></div></div>
                <div class="table-responsive"><table class="table table-dark table-hover">
                    <thead class="table-gold"><tr><th>Plano</th><th>Parcela Mensal</th><th>Valor Total</th><th>Taxa Admin</th><th>Ação</th></tr></thead>
                    <tbody>${this.plans.map(plan => this.renderPlanRow(plan, bestMonthly, bestTotal)).join('')}</tbody>
                </table></div>
                <div class="comparison-chart mt-4"><canvas id="comparisonChart" width="400" height="200"></canvas></div>`;
            this.renderChart();
        }
        renderPlanRow(plan, bestMonthly, bestTotal) {
            const isBestMonthly = plan.id === bestMonthly.id;
            const isBestTotal = plan.id === bestTotal.id;
            return `<tr class="${isBestMonthly || isBestTotal ? 'table-success' : ''}"><td><strong>${plan.name}</strong> ${isBestMonthly ? '<span class="badge bg-success ms-1">Menor Parcela</span>' : ''} ${isBestTotal ? '<span class="badge bg-warning ms-1">Menor Total</span>' : ''}</td><td>${formatter.format(plan.monthlyPayment)}</td><td>${formatter.format(plan.totalPlanValue)}</td><td>${(plan.adminRate * 100).toFixed(1)}%</td><td><button class="btn btn-sm btn-outline-gold" onclick="window.selectPlan(${plan.id})"><i class="bi bi-check-circle"></i> Selecionar</button></td></tr>`;
        }
        renderChart() {
            const ctx = document.getElementById('comparisonChart')?.getContext('2d');
            if (!ctx) return;
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: this.plans.map(p => p.name),
                    datasets: [{ label: 'Parcela Mensal (R$)', data: this.plans.map(p => p.monthlyPayment), backgroundColor: 'rgba(212, 175, 55, 0.6)', borderColor: 'rgba(212, 175, 55, 1)', borderWidth: 1 }, { label: 'Valor Total (R$)', data: this.plans.map(p => p.totalPlanValue), backgroundColor: 'rgba(33, 150, 243, 0.6)', borderColor: 'rgba(33, 150, 243, 1)', borderWidth: 1, yAxisID: 'y1' }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: 'Comparação de Planos de Consórcio', color: '#D4AF37' }, legend: { labels: { color: '#ffffff' } } }, scales: { y: { ticks: { color: '#ffffff' } }, y1: { type: 'linear', display: true, position: 'right', ticks: { color: '#ffffff' }, grid: { drawOnChartArea: false } }, x: { ticks: { color: '#ffffff' } } } }
            });
        }
    }

    class SmartRecommendations {
        constructor() { this.setupRecommendations(); }
        setupRecommendations() {
            document.querySelectorAll('.tab-pane[id$="-calculator"]').forEach(tab => this.addRecommendationPanel(tab));
        }
        addRecommendationPanel(tab) {
            if (tab.querySelector('.recommendations-panel')) return;
            const panel = document.createElement('div');
            panel.className = 'recommendations-panel mt-3';
            panel.innerHTML = `<div class="tool-card"><div class="tool-card-header"><h6 class="tool-card-title"><span class="tool-card-icon"><i class="bi bi-lightbulb"></i></span> Recomendações</h6></div><div class="tool-card-body"><div class="recommendations-content"><div class="loading-recommendations"><i class="bi bi-gear-fill spin"></i> Analisando...</div></div></div></div>`;
            tab.appendChild(panel);
            setTimeout(() => this.loadRecommendations(panel), 1500);
        }
        loadRecommendations(panel) {
            const content = panel.querySelector('.recommendations-content');
            const recommendations = this.generateRecommendations();
            content.innerHTML = `<div class="recommendations-list">${recommendations.map(rec => `<div class="recommendation-item ${rec.priority}"><div class="rec-icon"><i class="bi bi-${rec.icon}"></i></div><div class="rec-content"><h6>${rec.title}</h6><p>${rec.description}</p></div></div>`).join('')}</div>`;
        }
        generateRecommendations() {
            return [
                { title: 'Plano Otimizado', description: 'O plano de 60 meses oferece o melhor custo-benefício para seu perfil.', icon: 'award', priority: 'high' },
                { title: 'Economia Potencial', description: 'Você pode economizar até R$ 8.500 escolhendo o plano com taxa reduzida.', icon: 'piggy-bank', priority: 'medium' },
                { title: 'Dica de Vendas', description: 'Clientes com esse perfil têm 85% mais chance de aceitar propostas com entrada baixa.', icon: 'graph-up-arrow', priority: 'info' }
            ];
        }
    }

    // =======================================
    // SECTION 3: MAIN CALCULATOR MANAGER
    // (Combines logic from all files)
    // =======================================

    class CalculatorManager {
        constructor() {
            this.validationRules = {
                'carValue': { min: 10000, max: 500000, message: 'Valor entre R$ 10.000 e R$ 500.000' },
                'propertyValue': { min: 50000, max: 2000000, message: 'Valor entre R$ 50.000 e R$ 2.000.000' },
                'carRate': { min: 10, max: 25, message: 'Taxa entre 10% e 25%' },
                'propertyRate': { min: 8, max: 20, message: 'Taxa entre 8% e 20%' }
            };
            this.init();
        }

        init() {
            this.setupEventHandlers();
            this.restoreCalculatorState();
            this.setupKeyboardShortcuts();
            this.setupTooltips();
            this.setupAnimations();
            
            // Initialize advanced features if on the correct page
            if (window.location.pathname.includes('calculadoras')) {
                new ConsortiumComparator();
                new SmartRecommendations();
                // Placeholder for other advanced features if needed
            }

            notifications.info('Calculadoras Prontas!', 'Utilize as abas para navegar e simular.', 7000);
        }

        // --- Core Setup and State Management ---
        setupEventHandlers() {
            document.querySelectorAll('.calculator-form').forEach(form => {
                form.addEventListener('submit', e => e.preventDefault()); // Prevent default submission
                
                const calcButton = form.querySelector('button[id^="calculate"]');
                if(calcButton) {
                    calcButton.addEventListener('click', () => this.runCalculation(form));
                }

                form.querySelectorAll('input, select').forEach(input => {
                    input.addEventListener('change', () => {
                        this.runCalculation(form, false); // Recalculate on change
                        this.saveCalculatorState();
                    });
                    if (input.type === 'range') {
                        input.addEventListener('input', () => this.updateSliderValue(input));
                    }
                });
            });
            
            document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
                tab.addEventListener('shown.bs.tab', () => this.saveCalculatorState());
            });
        }

        runCalculation(form, animate = true) {
            if (!this.validateForm(form)) {
                notifications.error('Erro de Validação', 'Por favor, corrija os campos em vermelho.');
                return;
            }
            if (form.id.includes('car')) {
                this.calculateCarConsortium(animate);
            } else if (form.id.includes('property')) {
                this.calculatePropertyConsortium(animate);
            }
        }

        saveCalculatorState() {
            const state = {
                carValue: document.getElementById('carValue')?.value,
                carPlanDuration: document.getElementById('carPlanDuration')?.value,
                carRate: document.getElementById('carRate')?.value,
                carFundFee: document.getElementById('carFundFee')?.value,
                propertyValue: document.getElementById('propertyValue')?.value,
                propertyPlanDuration: document.getElementById('propertyPlanDuration')?.value,
                propertyRate: document.getElementById('propertyRate')?.value,
                propertyFundFee: document.getElementById('propertyFundFee')?.value,
                activeTabId: document.querySelector('.tab-pane.show.active')?.id
            };
            localStorage.setItem('lionsCalculadoraState', JSON.stringify(state));
        }

        restoreCalculatorState() {
            const savedState = localStorage.getItem('lionsCalculadoraState');
            if (savedState) {
                const state = JSON.parse(savedState);
                Object.entries(state).forEach(([key, value]) => {
                    if (key !== 'activeTabId') {
                        const element = document.getElementById(key);
                        if (element) {
                            element.value = value;
                            if (element.type === 'range') this.updateSliderValue(element);
                        }
                    }
                });

                if (state.activeTabId) {
                    const tabToActivate = document.querySelector(`[data-bs-target="#${state.activeTabId}"]`);
                    if (tabToActivate) new bootstrap.Tab(tabToActivate).show();
                }
                
                this.calculateCarConsortium(false);
                this.calculatePropertyConsortium(false);
            }
        }

        updateSliderValue(slider) {
            const valueDisplay = document.getElementById(`${slider.id}Value`);
            if (valueDisplay) valueDisplay.textContent = slider.value + '%';
        }

        // --- Calculation Logic ---
        calculateCarConsortium(animate = true) {
            const carValue = parseFloat(document.getElementById('carValue').value);
            const planDuration = parseInt(document.getElementById('carPlanDuration').value);
            const adminRate = parseFloat(document.getElementById('carRate').value) / 100;
            const fundFee = parseFloat(document.getElementById('carFundFee').value) / 100;
            
            const adminFeeTotal = carValue * adminRate;
            const fundFeeTotal = carValue * fundFee;
            const totalPlanValue = carValue + adminFeeTotal + fundFeeTotal;
            const monthlyPayment = totalPlanValue / planDuration;

            this.updateResults('car', { monthlyPayment, carValue, adminFeeTotal, fundFeeTotal, totalPlanValue, planDuration, adminRate }, animate);
        }

        calculatePropertyConsortium(animate = true) {
            const propertyValue = parseFloat(document.getElementById('propertyValue').value);
            const planDuration = parseInt(document.getElementById('propertyPlanDuration').value);
            const adminRate = parseFloat(document.getElementById('propertyRate').value) / 100;
            const fundFee = parseFloat(document.getElementById('propertyFundFee').value) / 100;

            const adminFeeTotal = propertyValue * adminRate;
            const fundFeeTotal = propertyValue * fundFee;
            const totalPlanValue = propertyValue + adminFeeTotal + fundFeeTotal;
            const monthlyPayment = totalPlanValue / planDuration;
            
            this.updateResults('property', { monthlyPayment, propertyValue, adminFeeTotal, fundFeeTotal, totalPlanValue, planDuration, adminRate }, animate);
        }

        updateResults(type, data, animate) {
            const { monthlyPayment, totalPlanValue, planDuration } = data;
            const creditValue = data.carValue || data.propertyValue;
            
            document.getElementById(`${type}MonthlyPayment`).textContent = formatter.format(monthlyPayment);
            document.getElementById(`${type}TotalCredit`).textContent = formatter.format(creditValue);
            document.getElementById(`${type}TotalAdminFee`).textContent = `${formatter.format(data.adminFeeTotal)} (${(data.adminRate * 100).toFixed(1)}%)`;
            document.getElementById(`${type}TotalFundFee`).textContent = formatter.format(data.fundFeeTotal);
            document.getElementById(`${type}TotalPlanValue`).textContent = formatter.format(totalPlanValue);

            const years = Math.floor(planDuration / 12);
            const months = planDuration % 12;
            document.getElementById(`${type}PlanDurationResult`).textContent = `${planDuration} meses (${years}a ${months > 0 ? months + 'm' : ''})`;

            if (animate) {
                const resultEl = document.getElementById(`${type}ResultPrincipal`);
                resultEl.classList.add('animar-resultado');
                setTimeout(() => resultEl.classList.remove('animar-resultado'), 700);
            }
            
            this.updateProposalFormData(type, data);
        }
        
        updateProposalFormData(type, data) {
            const creditValue = data.carValue || data.propertyValue;
            document.getElementById(`${type}ProposalCreditValue`).value = creditValue.toFixed(2);
            document.getElementById(`${type}ProposalDuration`).value = data.planDuration;
            document.getElementById(`${type}ProposalAdminRate`).value = (data.adminRate * 100).toFixed(2);
            document.getElementById(`${type}ProposalMonthlyPayment`).value = data.monthlyPayment.toFixed(2);
            document.getElementById(`${type}ProposalTotalValue`).value = data.totalPlanValue.toFixed(2);
        }

        // --- Validation ---
        validateForm(form) {
            let isValid = true;
            form.querySelectorAll('input[type="number"], input[type="range"]').forEach(input => {
                const rules = this.validationRules[input.id];
                if (rules) {
                    const value = parseFloat(input.value);
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
            field.classList.add('is-invalid');
            let errorDiv = field.parentNode.querySelector('.invalid-feedback');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                field.parentNode.appendChild(errorDiv);
            }
            errorDiv.textContent = message;
        }

        clearFieldError(field) {
            field.classList.remove('is-invalid');
            const errorDiv = field.parentNode.querySelector('.invalid-feedback');
            if (errorDiv) errorDiv.remove();
        }

        // --- UX/UI Enhancements ---
        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    const activeForm = document.querySelector('.tab-pane.active .calculator-form');
                    if (activeForm) this.runCalculation(activeForm);
                }
            });
        }

        setupTooltips() {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        }
        
        setupAnimations() {
            const cards = document.querySelectorAll('.tool-card, .result-card');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.animation = 'slideInUp 0.6s ease-out forwards';
                    }
                });
            }, { threshold: 0.1 });
            cards.forEach(card => observer.observe(card));
        }
    }

    // =======================================
    // SECTION 4: INITIALIZATION
    // =======================================
    
    new CalculatorManager();

    // =======================================
    // SECTION 5: DYNAMIC STYLES
    // =======================================
    
    const dynamicStyles = document.createElement('style');
    dynamicStyles.textContent = `
        /* Notifications */
        .notification-container { position: fixed; top: 20px; right: 20px; z-index: 1056; width: 350px; }
        .notification { background: #333; color: #fff; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); transition: all 0.3s ease; transform: translateX(110%); opacity: 0; }
        .notification.show { transform: translateX(0); opacity: 1; }
        .notification-header { display: flex; align-items: center; padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .notification-icon { font-size: 1.2rem; margin-right: 10px; }
        .notification-title { margin: 0; flex-grow: 1; font-size: 1rem; }
        .notification-close { background: none; border: none; color: #fff; opacity: 0.7; cursor: pointer; }
        .notification-content { padding: 12px; font-size: 0.9rem; }
        .notification.success { background: #28a745; }
        .notification.warning { background: #ffc107; color: #000; }
        .notification.error { background: #dc3545; }
        .notification.info { background: #17a2b8; }
        .notification-progress { height: 4px; background: rgba(255,255,255,0.5); animation: progress linear forwards; }
        @keyframes progress { from { width: 100%; } to { width: 0%; } }

        /* Calculator Animations & Styles */
        .animar-resultado { animation: flashGold 0.7s ease; }
        @keyframes flashGold { 0% { background-color: rgba(212, 175, 55, 0); } 50% { background-color: rgba(212, 175, 55, 0.3); } 100% { background-color: rgba(212, 175, 55, 0); } }
        .is-invalid { border-color: #dc3545 !important; }
        .invalid-feedback { color: #dc3545; font-size: 0.875em; margin-top: .25rem; display: block; }
        @keyframes slideInUp { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        
        /* Advanced Features Styles */
        .comparison-summary { display: flex; gap: 2rem; margin-top: 1rem; }
        .summary-item { display: flex; align-items: center; gap: 0.5rem; }
        .table-gold thead th { background: var(--color-gold); color: var(--color-dark); }
        .recommendations-list { display: flex; flex-direction: column; gap: 1rem; }
        .recommendation-item { display: flex; gap: 1rem; padding: 1rem; border-radius: 8px; border-left: 3px solid; }
        .recommendation-item.high { border-left-color: #4caf50; background: rgba(76, 175, 80, 0.1); }
        .recommendation-item.medium { border-left-color: #ff9800; background: rgba(255, 152, 0, 0.1); }
        .recommendation-item.info { border-left-color: #2196f3; background: rgba(33, 150, 243, 0.1); }
        .rec-icon { font-size: 1.5rem; color: var(--color-gold); }
    `;
    document.head.appendChild(dynamicStyles);
});
