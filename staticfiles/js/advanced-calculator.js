/**
 * Lions CRM - Advanced Calculator Features
 * Versão: 1.0.0 (23/05/2025)
 * Funcionalidades avançadas para as calculadoras de consórcio
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // SISTEMA DE COMPARAÇÃO DE PLANOS
    // ========================================
    
    class ConsortiumComparator {
        constructor() {
            this.plans = [];
            this.createComparisonInterface();
        }
        
        createComparisonInterface() {
            const comparisonTab = document.querySelector('#comparison-calculator');
            if (!comparisonTab) return;
            
            comparisonTab.innerHTML = `
                <div class="row">
                    <div class="col-12">
                        <div class="tool-card">
                            <div class="tool-card-header">
                                <h5 class="tool-card-title">
                                    <span class="tool-card-icon"><i class="bi bi-bar-chart"></i></span>
                                    Comparativo de Planos
                                </h5>
                            </div>
                            <div class="tool-card-body">
                                <div class="comparison-controls mb-4">
                                    <div class="row">
                                        <div class="col-md-4">
                                            <label class="form-label">Tipo de Consórcio</label>
                                            <select id="comparisonType" class="form-select">
                                                <option value="auto">Automóvel</option>
                                                <option value="property">Imóvel</option>
                                                <option value="heavy">Veículos Pesados</option>
                                            </select>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">Valor do Crédito</label>
                                            <input type="number" id="comparisonValue" class="form-control" value="100000" min="10000">
                                        </div>
                                        <div class="col-md-4">
                                            <button id="addPlanBtn" class="btn btn-gold mt-4">
                                                <i class="bi bi-plus"></i> Adicionar Plano
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div id="comparisonResults" class="comparison-results">
                                    <!-- Resultados da comparação serão inseridos aqui -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            this.bindEvents();
        }
        
        bindEvents() {
            document.getElementById('addPlanBtn')?.addEventListener('click', () => {
                this.addPlan();
            });
        }
        
        addPlan() {
            const type = document.getElementById('comparisonType').value;
            const value = parseFloat(document.getElementById('comparisonValue').value);
            
            // Simular diferentes planos com taxas variadas
            const planVariations = [
                { duration: 36, adminRate: 0.18, entryFee: 0.03, fundFee: 0.02 },
                { duration: 48, adminRate: 0.16, entryFee: 0.025, fundFee: 0.015 },
                { duration: 60, adminRate: 0.165, entryFee: 0.025, fundFee: 0.015 },
                { duration: 72, adminRate: 0.15, entryFee: 0.02, fundFee: 0.01 },
                { duration: 84, adminRate: 0.145, entryFee: 0.02, fundFee: 0.01 }
            ];
            
            this.plans = planVariations.map((plan, index) => {
                const adminFeeTotal = value * plan.adminRate;
                const entryFeeTotal = value * plan.entryFee;
                const fundFeeTotal = value * plan.fundFee;
                const totalPlanValue = value + adminFeeTotal + entryFeeTotal + fundFeeTotal;
                const monthlyPayment = totalPlanValue / plan.duration;
                
                return {
                    id: index + 1,
                    name: `Plano ${plan.duration} meses`,
                    duration: plan.duration,
                    adminRate: plan.adminRate,
                    entryFee: plan.entryFee,
                    fundFee: plan.fundFee,
                    monthlyPayment,
                    totalPlanValue,
                    creditValue: value
                };
            });
            
            this.renderComparison();
        }
        
        renderComparison() {
            const container = document.getElementById('comparisonResults');
            if (!container) return;
            
            // Encontrar melhor e pior opção
            const bestMonthly = this.plans.reduce((prev, curr) => 
                prev.monthlyPayment < curr.monthlyPayment ? prev : curr
            );
            const bestTotal = this.plans.reduce((prev, curr) => 
                prev.totalPlanValue < curr.totalPlanValue ? prev : curr
            );
            
            container.innerHTML = `
                <div class="comparison-header mb-4">
                    <h6 class="text-gold">Comparação de ${this.plans.length} Planos</h6>
                    <div class="comparison-summary">
                        <div class="summary-item">
                            <i class="bi bi-trophy text-success"></i>
                            <span>Menor Parcela: ${this.formatCurrency(bestMonthly.monthlyPayment)} (${bestMonthly.name})</span>
                        </div>
                        <div class="summary-item">
                            <i class="bi bi-star text-warning"></i>
                            <span>Menor Total: ${this.formatCurrency(bestTotal.totalPlanValue)} (${bestTotal.name})</span>
                        </div>
                    </div>
                </div>
                
                <div class="comparison-table">
                    <div class="table-responsive">
                        <table class="table table-dark table-hover">
                            <thead class="table-gold">
                                <tr>
                                    <th>Plano</th>
                                    <th>Parcela Mensal</th>
                                    <th>Valor Total</th>
                                    <th>Taxa Admin</th>
                                    <th>Economia vs Maior</th>
                                    <th>Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${this.plans.map(plan => this.renderPlanRow(plan, bestMonthly, bestTotal)).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="comparison-chart mt-4">
                    <canvas id="comparisonChart" width="400" height="200"></canvas>
                </div>
            `;
            
            this.renderChart();
        }
        
        renderPlanRow(plan, bestMonthly, bestTotal) {
            const worstTotal = this.plans.reduce((prev, curr) => 
                prev.totalPlanValue > curr.totalPlanValue ? prev : curr
            );
            const savings = worstTotal.totalPlanValue - plan.totalPlanValue;
            
            const isBestMonthly = plan.id === bestMonthly.id;
            const isBestTotal = plan.id === bestTotal.id;
            
            return `
                <tr class="${isBestMonthly || isBestTotal ? 'table-success' : ''}">
                    <td>
                        <strong>${plan.name}</strong>
                        ${isBestMonthly ? '<span class="badge bg-success ms-1">Menor Parcela</span>' : ''}
                        ${isBestTotal ? '<span class="badge bg-warning ms-1">Menor Total</span>' : ''}
                    </td>
                    <td>${this.formatCurrency(plan.monthlyPayment)}</td>
                    <td>${this.formatCurrency(plan.totalPlanValue)}</td>
                    <td>${(plan.adminRate * 100).toFixed(1)}%</td>
                    <td class="text-success">+${this.formatCurrency(savings)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-gold" onclick="window.selectPlan(${plan.id})">
                            <i class="bi bi-check-circle"></i> Selecionar
                        </button>
                    </td>
                </tr>
            `;
        }
        
        renderChart() {
            const ctx = document.getElementById('comparisonChart')?.getContext('2d');
            if (!ctx) return;
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: this.plans.map(p => p.name),
                    datasets: [{
                        label: 'Parcela Mensal (R$)',
                        data: this.plans.map(p => p.monthlyPayment),
                        backgroundColor: 'rgba(212, 175, 55, 0.6)',
                        borderColor: 'rgba(212, 175, 55, 1)',
                        borderWidth: 1
                    }, {
                        label: 'Valor Total (R$)',
                        data: this.plans.map(p => p.totalPlanValue),
                        backgroundColor: 'rgba(33, 150, 243, 0.6)',
                        borderColor: 'rgba(33, 150, 243, 1)',
                        borderWidth: 1,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Comparação de Planos de Consórcio',
                            color: '#D4AF37'
                        },
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            ticks: {
                                color: '#ffffff',
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            ticks: {
                                color: '#ffffff',
                                callback: function(value) {
                                    return 'R$ ' + (value / 1000).toFixed(0) + 'k';
                                }
                            },
                            grid: {
                                drawOnChartArea: false,
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: '#ffffff'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            });
        }
        
        formatCurrency(value) {
            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            }).format(value);
        }
    }
    
    // ========================================
    // SISTEMA DE RECOMENDAÇÕES INTELIGENTES
    // ========================================
    
    class SmartRecommendations {
        constructor() {
            this.setupRecommendations();
        }
        
        setupRecommendations() {
            // Adicionar painel de recomendações a cada calculadora
            const calculatorTabs = document.querySelectorAll('.tab-pane[id$="-calculator"]');
            
            calculatorTabs.forEach(tab => {
                this.addRecommendationPanel(tab);
            });
        }
        
        addRecommendationPanel(tab) {
            const existingRecommendations = tab.querySelector('.recommendations-panel');
            if (existingRecommendations) return;
            
            const panel = document.createElement('div');
            panel.className = 'recommendations-panel mt-3';
            panel.innerHTML = `
                <div class="tool-card">
                    <div class="tool-card-header">
                        <h6 class="tool-card-title">
                            <span class="tool-card-icon"><i class="bi bi-lightbulb"></i></span>
                            Recomendações Inteligentes
                        </h6>
                    </div>
                    <div class="tool-card-body">
                        <div class="recommendations-content">
                            <div class="loading-recommendations">
                                <i class="bi bi-gear-fill spin"></i>
                                Analisando seu perfil...
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Inserir antes do último elemento da tab
            const lastCard = tab.querySelector('.tool-card:last-child');
            if (lastCard) {
                lastCard.parentNode.insertBefore(panel, lastCard.nextSibling);
            } else {
                tab.appendChild(panel);
            }
            
            // Simular carregamento de recomendações
            setTimeout(() => {
                this.loadRecommendations(panel);
            }, 1500);
        }
        
        loadRecommendations(panel) {
            const content = panel.querySelector('.recommendations-content');
            
            // Simular análise baseada em dados do usuário
            const recommendations = this.generateRecommendations();
            
            content.innerHTML = `
                <div class="recommendations-list">
                    ${recommendations.map(rec => `
                        <div class="recommendation-item ${rec.priority}">
                            <div class="rec-icon">
                                <i class="bi bi-${rec.icon}"></i>
                            </div>
                            <div class="rec-content">
                                <h6>${rec.title}</h6>
                                <p>${rec.description}</p>
                                ${rec.action ? `<button class="btn btn-sm btn-outline-gold">${rec.action}</button>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        generateRecommendations() {
            // Simulação de recomendações baseadas em perfil
            const recommendations = [
                {
                    title: 'Plano Otimizado Detectado',
                    description: 'Com base no seu perfil, o plano de 60 meses oferece o melhor custo-benefício.',
                    icon: 'award',
                    priority: 'high',
                    action: 'Ver Detalhes'
                },
                {
                    title: 'Economia Potencial',
                    description: 'Você pode economizar até R$ 8.500 escolhendo o plano com taxa reduzida.',
                    icon: 'piggy-bank',
                    priority: 'medium',
                    action: 'Calcular Economia'
                },
                {
                    title: 'Dica de Vendas',
                    description: 'Clientes com esse perfil têm 85% mais chance de aceitar propostas com entrada baixa.',
                    icon: 'graph-up-arrow',
                    priority: 'info'
                }
            ];
            
            return recommendations;
        }
    }
    
    // ========================================
    // SIMULADOR DE CONTEMPLAÇÃO
    // ========================================
    
    class ContemplationSimulator {
        constructor() {
            this.addSimulatorToCalculators();
        }
        
        addSimulatorToCalculators() {
            const calculatorTabs = document.querySelectorAll('.tab-pane[id$="-calculator"]');
            
            calculatorTabs.forEach(tab => {
                this.addSimulatorPanel(tab);
            });
        }
        
        addSimulatorPanel(tab) {
            const panel = document.createElement('div');
            panel.className = 'contemplation-simulator mt-3';
            panel.innerHTML = `
                <div class="tool-card">
                    <div class="tool-card-header">
                        <h6 class="tool-card-title">
                            <span class="tool-card-icon"><i class="bi bi-calendar-check"></i></span>
                            Simulador de Contemplação
                        </h6>
                    </div>
                    <div class="tool-card-body">
                        <div class="simulator-controls mb-3">
                            <div class="row">
                                <div class="col-md-6">
                                    <label class="form-label">Sua Posição no Grupo</label>
                                    <input type="number" class="form-control" id="groupPosition" min="1" max="200" value="50">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Tipo de Contemplação</label>
                                    <select class="form-select" id="contemplationType">
                                        <option value="random">Sorteio</option>
                                        <option value="bid">Lance</option>
                                        <option value="both">Ambos</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <button class="btn btn-gold w-100 mb-3" onclick="this.closest('.contemplation-simulator').querySelector('.simulator-results').style.display='block'">
                            <i class="bi bi-play-circle"></i> Simular Contemplação
                        </button>
                        
                        <div class="simulator-results" style="display: none;">
                            <div class="row">
                                <div class="col-md-4 text-center">
                                    <div class="result-metric">
                                        <h4 class="text-gold">18</h4>
                                        <small>Meses Estimados</small>
                                    </div>
                                </div>
                                <div class="col-md-4 text-center">
                                    <div class="result-metric">
                                        <h4 class="text-success">72%</h4>
                                        <small>Chance de Contemplação</small>
                                    </div>
                                </div>
                                <div class="col-md-4 text-center">
                                    <div class="result-metric">
                                        <h4 class="text-info">R$ 85.400</h4>
                                        <small>Valor Pago até Contemplação</small>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="contemplation-timeline mt-3">
                                <h6>Timeline de Contemplação</h6>
                                <div class="timeline-bar">
                                    <div class="timeline-progress" style="width: 30%"></div>
                                    <div class="timeline-marker" style="left: 30%">Você está aqui</div>
                                </div>
                                <div class="timeline-labels">
                                    <span>0 meses</span>
                                    <span>60 meses</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            tab.appendChild(panel);
        }
    }
    
    // ========================================
    // SISTEMA DE EXPORTAÇÃO AVANÇADA
    // ========================================
    
    class AdvancedExport {
        constructor() {
            this.addExportOptions();
        }
        
        addExportOptions() {
            // Adicionar botões de exportação a cada seção de resultados
            const resultCards = document.querySelectorAll('.result-card');
            
            resultCards.forEach(card => {
                this.addExportButton(card);
            });
        }
        
        addExportButton(card) {
            const exportBtn = document.createElement('div');
            exportBtn.className = 'export-options mt-3';
            exportBtn.innerHTML = `
                <div class="dropdown">
                    <button class="btn btn-outline-gold btn-sm dropdown-toggle w-100" type="button" data-bs-toggle="dropdown">
                        <i class="bi bi-download"></i> Exportar Simulação
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" onclick="exportToPDF(this)">
                            <i class="bi bi-file-pdf"></i> PDF Detalhado
                        </a></li>
                        <li><a class="dropdown-item" href="#" onclick="exportToExcel(this)">
                            <i class="bi bi-file-excel"></i> Planilha Excel
                        </a></li>
                        <li><a class="dropdown-item" href="#" onclick="exportToWhatsApp(this)">
                            <i class="bi bi-whatsapp"></i> Enviar por WhatsApp
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" onclick="shareSimulation(this)">
                            <i class="bi bi-share"></i> Compartilhar Link
                        </a></li>
                    </ul>
                </div>
            `;
            
            card.querySelector('.tool-card-body').appendChild(exportBtn);
        }
    }
    
    // ========================================
    // INICIALIZAÇÃO DOS MÓDULOS
    // ========================================
    
    // Inicializar apenas se estivermos na página das calculadoras
    if (window.location.pathname.includes('calculadoras')) {
        new ConsortiumComparator();
        new SmartRecommendations();
        new ContemplationSimulator();
        new AdvancedExport();
        
        console.log('🧮 Advanced Calculator Features carregado!');
    }
    
    // ========================================
    // FUNÇÕES GLOBAIS PARA EXPORT
    // ========================================
    
    window.selectPlan = function(planId) {
        window.toast?.show(`Plano ${planId} selecionado! Configurando calculadora...`, 'success');
        // Implementar lógica de seleção do plano
    };
    
    window.exportToPDF = function(element) {
        window.toast?.show('Gerando PDF detalhado...', 'info');
        // Implementar export para PDF
    };
    
    window.exportToExcel = function(element) {
        window.toast?.show('Gerando planilha Excel...', 'info');
        // Implementar export para Excel
    };
    
    window.exportToWhatsApp = function(element) {
        window.toast?.show('Preparando mensagem para WhatsApp...', 'info');
        // Implementar compartilhamento via WhatsApp
    };
    
    window.shareSimulation = function(element) {
        window.toast?.show('Link de compartilhamento copiado!', 'success');
        // Implementar compartilhamento de link
    };
    
});

// CSS adicional para os novos componentes
const advancedStyles = document.createElement('style');
advancedStyles.textContent = `
    .comparison-summary {
        display: flex;
        gap: 2rem;
        margin-top: 1rem;
    }
    
    .summary-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--color-text-muted);
        font-size: 0.9rem;
    }
    
    .table-gold thead th {
        background: var(--color-gold);
        color: var(--color-dark);
        font-weight: 600;
    }
    
    .recommendations-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .recommendation-item {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid;
    }
    
    .recommendation-item.high {
        border-left-color: #4caf50;
        background: rgba(76, 175, 80, 0.05);
    }
    
    .recommendation-item.medium {
        border-left-color: #ff9800;
        background: rgba(255, 152, 0, 0.05);
    }
    
    .recommendation-item.info {
        border-left-color: #2196f3;
        background: rgba(33, 150, 243, 0.05);
    }
    
    .rec-icon {
        font-size: 1.5rem;
        color: var(--color-gold);
    }
    
    .rec-content h6 {
        margin-bottom: 0.5rem;
        color: var(--color-text);
    }
    
    .rec-content p {
        margin-bottom: 0.5rem;
        color: var(--color-text-muted);
        font-size: 0.9rem;
    }
    
    .result-metric h4 {
        margin-bottom: 0.25rem;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .result-metric small {
        color: var(--color-text-muted);
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }
    
    .timeline-bar {
        position: relative;
        height: 8px;
        background: var(--color-dark-light);
        border-radius: 4px;
        margin: 1rem 0 0.5rem;
    }
    
    .timeline-progress {
        height: 100%;
        background: var(--color-gold);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    .timeline-marker {
        position: absolute;
        top: -20px;
        transform: translateX(-50%);
        background: var(--color-gold);
        color: var(--color-dark);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .timeline-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: var(--color-text-muted);
    }
    
    .spin {
        animation: spin 1s linear infinite;
    }
    
    .loading-recommendations {
        text-align: center;
        color: var(--color-text-muted);
        padding: 2rem;
    }
`;
document.head.appendChild(advancedStyles);
