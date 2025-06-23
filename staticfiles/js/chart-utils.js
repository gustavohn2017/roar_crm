/**
 * Roar CRM - Chart Utilities
 * Scripts para configuração e personalização de gráficos no painel administrativo
 */

// Configuração global para todos os gráficos
Chart.defaults.color = '#e0e0e0';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

// Paletas de cores padrão
const CHART_COLORS = {
    gold: 'rgba(212, 175, 55, 0.8)',
    goldLight: 'rgba(230, 193, 88, 0.8)',
    goldDark: 'rgba(170, 140, 44, 0.8)',
    orange: 'rgba(255, 152, 0, 0.8)',
    blue: 'rgba(33, 150, 243, 0.8)',
    green: 'rgba(76, 175, 80, 0.8)',
    red: 'rgba(207, 102, 121, 0.8)',
    purple: 'rgba(156, 39, 176, 0.8)',
    cyan: 'rgba(0, 188, 212, 0.8)',
    yellow: 'rgba(255, 235, 59, 0.8)',
};

// Array de cores para uso em gráficos
const chartColorArray = [
    CHART_COLORS.gold,
    CHART_COLORS.goldLight,
    CHART_COLORS.goldDark,
    CHART_COLORS.orange,
    CHART_COLORS.blue,
    CHART_COLORS.green,
    CHART_COLORS.red,
    CHART_COLORS.purple,
    CHART_COLORS.cyan,
    CHART_COLORS.yellow,
];

/**
 * Cria um gráfico de barras
 * @param {string} elementId - ID do elemento canvas
 * @param {object} data - Dados para o gráfico
 * @param {object} options - Opções adicionais
 */
function createBarChart(elementId, data, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const defaultOptions = {
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
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
                display: Boolean(options.showLegend)
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: chartOptions
    });
}

/**
 * Cria um gráfico de linha
 * @param {string} elementId - ID do elemento canvas
 * @param {object} data - Dados para o gráfico
 * @param {object} options - Opções adicionais
 */
function createLineChart(elementId, data, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const defaultOptions = {
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: chartOptions
    });
}

/**
 * Cria um gráfico de pizza ou rosca
 * @param {string} elementId - ID do elemento canvas
 * @param {object} data - Dados para o gráfico
 * @param {object} options - Opções adicionais
 * @param {boolean} isDoughnut - Se true, cria um gráfico de rosca, caso contrário um gráfico de pizza
 */
function createPieChart(elementId, data, options = {}, isDoughnut = false) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const defaultOptions = {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: options.legendPosition || 'right'
            }
        }
    };
    
    if (isDoughnut) {
        defaultOptions.cutout = options.cutout || '60%';
    }
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: isDoughnut ? 'doughnut' : 'pie',
        data: data,
        options: chartOptions
    });
}

/**
 * Cria um gráfico de indicador tipo gauge
 * @param {string} elementId - ID do elemento canvas
 * @param {number} value - Valor a ser exibido (0-100)
 * @param {object} options - Opções adicionais
 */
function createGaugeChart(elementId, value, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Determina a cor com base no valor
    let color;
    if (value > 100) {
        color = CHART_COLORS.green;
    } else if (value >= 70) {
        color = CHART_COLORS.orange;
    } else {
        color = CHART_COLORS.red;
    }
    
    const chartData = {
        labels: ['Valor', 'Restante'],
        datasets: [{
            data: [value, value < 100 ? 100 - value : 0],
            backgroundColor: [
                color,
                'rgba(50, 50, 50, 0.2)'
            ],
            borderWidth: 0
        }]
    };
    
    const defaultOptions = {
        maintainAspectRatio: true,
        cutout: '75%',
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                enabled: false
            }
        }
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: chartOptions
    });
}
