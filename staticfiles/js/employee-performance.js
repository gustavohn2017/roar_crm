/**
 * Roar CRM - Advanced Employee Performance Charts
 * Provides functionality for individualized employee performance visualization
 */

class EmployeePerformanceCharts {
    constructor(options = {}) {
        // Chart colors from CSS variables
        this.colors = {
            gold: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-1') || '#d4af37',
            goldLight: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-2') || '#e6c158',
            goldDark: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-3') || '#aa8c2c',
            orange: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-4') || '#ff9800',
            blue: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-5') || '#2196f3',
            green: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-6') || '#4caf50',
            red: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-7') || '#f44336',
            purple: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-8') || '#9c27b0'
        };
        
        // Chart defaults
        this.defaults = {
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
            gridColor: 'rgba(255, 255, 255, 0.05)',
            animationDuration: 1000
        };
        
        // Merge provided options with defaults
        this.options = {...this.defaults, ...options};
    }
    
    /**
     * Initialize all employee performance charts on the dashboard
     */
    initDashboardCharts() {
        // Configure global Chart.js settings
        this._configureChartDefaults();
        
        // Initialize employee comparison chart if exists
        const employeeComparisonEl = document.getElementById('employeeComparisonChart');
        if (employeeComparisonEl) {
            this.renderEmployeeComparisonChart(employeeComparisonEl);
        }
        
        // Initialize all individual employee charts
        document.querySelectorAll('.employee-performance-chart').forEach(chartEl => {
            const chartType = chartEl.dataset.chartType;
            const employeeId = chartEl.dataset.employeeId;
            
            if (chartType === 'contacts') {
                this.renderEmployeeContactsChart(chartEl, employeeId);
            } else if (chartType === 'success-rate') {
                this.renderEmployeeSuccessRateChart(chartEl, employeeId);
            } else if (chartType === 'conversion') {
                this.renderEmployeeConversionChart(chartEl, employeeId);
            }
        });
    }
    
    /**
     * Configure global Chart.js settings
     * @private
     */
    _configureChartDefaults() {
        Chart.defaults.color = '#9e9e9e';
        Chart.defaults.font.family = this.options.fontFamily;
        Chart.defaults.scale.grid.color = this.options.gridColor;
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(17, 17, 17, 0.9)';
        Chart.defaults.plugins.tooltip.titleColor = this.colors.gold;
        Chart.defaults.plugins.tooltip.bodyColor = '#ffffff';
        Chart.defaults.plugins.tooltip.borderColor = this.colors.goldDark;
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.padding = 10;
        Chart.defaults.plugins.tooltip.cornerRadius = 6;
    }
    
    /**
     * Render a chart comparing all employees' performance metrics
     * @param {HTMLElement} chartElement - Canvas element
     */
    renderEmployeeComparisonChart(chartElement) {
        try {
            // Get employee data from the data attribute
            const employeeData = JSON.parse(chartElement.dataset.employees);
            
            // Prepare data
            const labels = employeeData.map(e => e.name);
            const contactsData = employeeData.map(e => e.contactCount);
            const successRateData = employeeData.map(e => e.successRate);
            const convertedLeadsData = employeeData.map(e => e.convertedLeads);
            
            // Create chart
            new Chart(chartElement, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Contatos',
                            data: contactsData,
                            backgroundColor: this.colors.gold,
                            borderColor: this.colors.goldDark,
                            borderWidth: 1
                        },
                        {
                            label: 'Taxa de Sucesso (%)',
                            data: successRateData,
                            backgroundColor: this.colors.green,
                            borderColor: 'rgba(76, 175, 80, 0.8)',
                            borderWidth: 1
                        },
                        {
                            label: 'Leads Convertidos',
                            data: convertedLeadsData,
                            backgroundColor: this.colors.blue,
                            borderColor: 'rgba(33, 150, 243, 0.8)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: this.options.animationDuration
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value;
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            align: 'end',
                            labels: {
                                boxWidth: 15,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y;
                                    
                                    if (label.includes('Taxa')) {
                                        return `${label}: ${value}%`;
                                    }
                                    
                                    return `${label}: ${value}`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error rendering employee comparison chart:', error);
        }
    }
    
    /**
     * Render a chart showing an employee's contact history
     * @param {HTMLElement} chartElement - Canvas element
     * @param {string} employeeId - Employee ID 
     */
    renderEmployeeContactsChart(chartElement, employeeId) {
        try {
            // Get contact data from the data attribute
            const contactsData = JSON.parse(chartElement.dataset.contacts);
            
            // Prepare data
            const labels = contactsData.map(d => d.dia);
            const contacts = contactsData.map(d => d.contatos);
            
            // Create chart
            new Chart(chartElement.querySelector('canvas'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Contatos',
                        data: contacts,
                        backgroundColor: 'rgba(212, 175, 55, 0.2)',
                        borderColor: this.colors.gold,
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: this.colors.goldLight,
                        pointBorderColor: this.colors.goldDark,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: this.options.animationDuration
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        } catch (error) {
            console.error(`Error rendering contacts chart for employee ${employeeId}:`, error);
        }
    }
    
    /**
     * Render a chart showing an employee's success rate
     * @param {HTMLElement} chartElement - Canvas element
     * @param {string} employeeId - Employee ID 
     */
    renderEmployeeSuccessRateChart(chartElement, employeeId) {
        try {
            // Get results data from the data attribute
            const resultsData = JSON.parse(chartElement.dataset.results);
            
            // Prepare data
            const labels = resultsData.map(d => d.resultado);
            const values = resultsData.map(d => d.total);
            const backgroundColor = [
                this.colors.green,  // Sucesso
                this.colors.orange, // Não Atendeu
                this.colors.blue,   // Ocupado
                this.colors.red,    // Número Inválido
                this.colors.purple  // Outro
            ];
            
            // Create chart
            new Chart(chartElement.querySelector('canvas'), {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: backgroundColor,
                        borderColor: 'rgba(26, 26, 26, 1)',
                        borderWidth: 1,
                        hoverOffset: 15
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: this.options.animationDuration
                    },
                    cutout: '60%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                padding: 20,
                                boxWidth: 12,
                                usePointStyle: true,
                                pointStyle: 'rectRounded'
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error(`Error rendering success rate chart for employee ${employeeId}:`, error);
        }
    }
    
    /**
     * Render a chart showing an employee's lead conversion
     * @param {HTMLElement} chartElement - Canvas element
     * @param {string} employeeId - Employee ID 
     */
    renderEmployeeConversionChart(chartElement, employeeId) {
        try {
            // Get conversion data from the data attribute
            const conversionRate = parseFloat(chartElement.dataset.conversionRate);
            const designatedLeads = parseInt(chartElement.dataset.designatedLeads);
            const convertedLeads = parseInt(chartElement.dataset.convertedLeads);
            
            // Create gauge chart
            new Chart(chartElement.querySelector('canvas'), {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [conversionRate, conversionRate < 100 ? 100 - conversionRate : 0],
                        backgroundColor: [
                            conversionRate > 50 ? this.colors.green : 
                            conversionRate > 30 ? this.colors.orange : this.colors.red,
                            'rgba(50, 50, 50, 0.2)'
                        ],
                        borderWidth: 0,
                        circumference: 180,
                        rotation: 270
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: this.options.animationDuration
                    },
                    cutout: '75%',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            enabled: false
                        }
                    }
                }
            });
            
            // Add stats to the chart's info container
            const statsContainer = chartElement.querySelector('.conversion-stats');
            if (statsContainer) {
                statsContainer.innerHTML = `
                    <div class="conversion-stats-item">
                        <span class="stats-value">${convertedLeads}</span>
                        <span class="stats-label">Leads Convertidos</span>
                    </div>
                    <div class="conversion-stats-item">
                        <span class="stats-value">${designatedLeads}</span>
                        <span class="stats-label">Leads Designados</span>
                    </div>
                    <div class="conversion-stats-item">
                        <span class="stats-value">${conversionRate}%</span>
                        <span class="stats-label">Taxa de Conversão</span>
                    </div>
                `;
            }
        } catch (error) {
            console.error(`Error rendering conversion chart for employee ${employeeId}:`, error);
        }
    }
    
    /**
     * Renderiza um gráfico gauge com suporte a métricas de desempenho
     * @param {HTMLElement} chartElement - Elemento do canvas 
     * @param {Object} options - Configurações do gráfico
     */
    renderGaugeChart(chartElement, options) {
        try {
            const defaultOptions = {
                min: 0,
                max: 100,
                value: 0,
                segments: [
                    { value: 25, color: this.colors.red },
                    { value: 50, color: this.colors.orange },
                    { value: 75, color: this.colors.goldLight },
                    { value: 100, color: this.colors.green }
                ],
                label: 'Desempenho',
                units: '%',
                showValue: true
            };
            
            const config = {...defaultOptions, ...options};
            
            // Verificar se Chart.js suporta o tipo gauge
            if (!Chart.controllers.gauge) {
                console.error('Chart.js não tem suporte para gráficos do tipo gauge. É necessário incluir um plugin.');
                return;
            }
            
            new Chart(chartElement, {
                type: 'gauge',
                data: {
                    datasets: [{
                        value: config.value,
                        data: config.segments.map(s => s.value),
                        backgroundColor: config.segments.map(s => s.color),
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: 20
                    },
                    needle: {
                        radiusPercentage: 2,
                        widthPercentage: 3.2,
                        lengthPercentage: 80,
                        color: 'rgba(255, 255, 255, 0.9)'
                    },
                    valueLabel: {
                        display: config.showValue,
                        fontSize: 20,
                        color: '#fff',
                        formatter: function(value) {
                            return value + config.units;
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            enabled: false
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error rendering gauge chart:', error);
        }
    }
    
    /**
     * Renderiza os gráficos específicos da página de detalhes do funcionário
     * @param {Object} employeeData - Dados do funcionário
     */
    renderEmployeeDetailsCharts(employeeData) {
        try {
            // Configurar gráfico de desempenho com pontuação por atividade
            const productivityLabels = employeeData.periodLabels || ["Jan", "Fev", "Mar", "Abr", "Mai"];
            
            // Pontuação geral do funcionário vs meta por período
            const performanceChart = document.getElementById('employeePerformanceChart');
            if (performanceChart) {
                new Chart(performanceChart, {
                    type: 'line',
                    data: {
                        labels: productivityLabels,
                        datasets: [
                            {
                                label: 'Desempenho Real',
                                data: employeeData.performance || [80, 85, 70, 90, 95],
                                borderColor: this.colors.gold,
                                backgroundColor: 'rgba(212, 175, 55, 0.2)',
                                fill: true,
                                tension: 0.4
                            },
                            {
                                label: 'Meta',
                                data: employeeData.target || [75, 75, 80, 80, 85],
                                borderColor: 'rgba(125, 125, 125, 0.6)',
                                backgroundColor: 'rgba(125, 125, 125, 0.1)',
                                borderDash: [5, 5],
                                fill: false,
                                tension: 0.1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Evolução do Desempenho',
                                color: '#e0e0e0'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                min: 50,
                                max: 100,
                                title: {
                                    display: true,
                                    text: 'Pontuação'
                                }
                            }
                        }
                    }
                });
            }
            
            // Gráfico de efetividade do funcionário (taxa de conversão comparativa)
            const effectivenessChart = document.getElementById('employeeEffectivenessChart');
            if (effectivenessChart) {
                new Chart(effectivenessChart, {
                    type: 'radar',
                    data: {
                        labels: ['Contatos', 'Taxa de Sucesso', 'Conversão', 'Follow-ups', 'Qualidade'],
                        datasets: [
                            {
                                label: 'Funcionário',
                                data: employeeData.effectiveness || [90, 85, 65, 75, 80],
                                backgroundColor: 'rgba(212, 175, 55, 0.3)',
                                borderColor: this.colors.goldLight,
                                borderWidth: 2,
                                pointBackgroundColor: this.colors.gold,
                                pointRadius: 4,
                                pointHoverRadius: 6
                            },
                            {
                                label: 'Média da Equipe',
                                data: employeeData.teamAverage || [70, 70, 70, 70, 70],
                                backgroundColor: 'rgba(150, 150, 150, 0.2)',
                                borderColor: 'rgba(150, 150, 150, 0.6)',
                                borderWidth: 2,
                                pointBackgroundColor: 'rgba(150, 150, 150, 0.7)',
                                pointRadius: 3
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'top'
                            }
                        },
                        scales: {
                            r: {
                                min: 0,
                                max: 100,
                                ticks: {
                                    stepSize: 20,
                                    backdropColor: 'rgba(0, 0, 0, 0)'
                                },
                                angleLines: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                },
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                },
                                pointLabels: {
                                    color: '#e0e0e0'
                                }
                            }
                        }
                    }
                });
            }
        } catch (error) {
            console.error('Error rendering employee details charts:', error);
        }
    }
}

// Initialize charts when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const performanceCharts = new EmployeePerformanceCharts();
    performanceCharts.initDashboardCharts();
});
