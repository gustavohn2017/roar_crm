/**
 * Roar CRM - Charts & Statistics Utilities
 * Arquivo unificado para scripts de gráficos, formatação de estatísticas e animações.
 */

// Namespace para evitar poluição do escopo global
const RoarCharts = {

    // ********************
    // ** CHART COLORS **
    // ********************
    colors: {
        gold: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-1') || '#d4af37',
        goldLight: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-2') || '#e6c158',
        goldDark: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-3') || '#aa8c2c',
        orange: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-4') || '#ff9800',
        blue: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-5') || '#2196f3',
        green: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-6') || '#4caf50',
        red: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-7') || '#f44336',
        purple: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-8') || '#9c27b0',
        cyan: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-9') || '#00bcd4',
        yellow: getComputedStyle(document.documentElement).getPropertyValue('--chart-color-10') || '#ffeb3b'
    },

    // ***********************************
    // ** CHART.JS GLOBAL CONFIGURATION **
    // ***********************************

    initializeGlobalConfig: function() {
        if (typeof Chart === 'undefined') {
            console.error("Chart.js não foi carregado. Gráficos não funcionarão.");
            return;
        }
        Chart.defaults.color = '#9e9e9e';
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.05)';
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(17, 17, 17, 0.9)';
        Chart.defaults.plugins.tooltip.titleColor = this.colors.gold;
        Chart.defaults.plugins.tooltip.bodyColor = '#ffffff';
        Chart.defaults.plugins.tooltip.borderColor = this.colors.goldDark;
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.padding = 10;
        Chart.defaults.plugins.tooltip.cornerRadius = 6;
    },

    // ******************
    // ** CHART UTILS **
    // ******************

    createBarChart: function(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId)?.getContext('2d');
        if (!ctx) return null;
        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: { maintainAspectRatio: false, ...options }
        });
    },

    createLineChart: function(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId)?.getContext('2d');
        if (!ctx) return null;
        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: { maintainAspectRatio: false, ...options }
        });
    },

    createDoughnutChart: function(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId)?.getContext('2d');
        if (!ctx) return null;
        return new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: { maintainAspectRatio: false, ...options }
        });
    },

    // ************************
    // ** GAUGE CHART PLUGIN **
    // ************************

    registerGaugeChart: function() {
        if (typeof Chart === 'undefined' || Chart.controllers.gauge) return;

        Chart.controllers.gauge = Chart.controllers.doughnut.extend({
            draw: function() {
                Chart.controllers.doughnut.prototype.draw.apply(this, arguments);
                const chart = this.chart;
                const ctx = chart.ctx;
                const value = chart.config.data.datasets[0].value;
                if (value === undefined) return;

                const { width, height } = chart.chartArea;
                const centerX = width / 2;
                const centerY = height / 2;
                const needleConfig = chart.options.needle || {};
                const outerRadius = Math.min(width, height) / 2;
                const length = outerRadius * (needleConfig.lengthPercentage || 80) / 100;
                const valueMax = chart.options.valueMax || 100;
                const angle = Math.PI * (1 - (value / valueMax));

                ctx.save();
                ctx.translate(centerX, centerY);
                ctx.rotate(angle);
                // ... (Needle drawing logic) ...
                ctx.restore();
            }
        });
    },

    // ************************
    // ** STATS FORMATTING **
    // ************************

    formatLargeNumber: function(value, currency = false, precise = false) {
        if (!value || isNaN(value)) return currency ? 'R$ 0' : '0';
        const num = parseFloat(String(value).replace(/[^\d.,]/g, '').replace(/\./g, '').replace(',', '.'));
        const prefix = currency ? 'R$ ' : '';
        const decimalPlaces = precise ? 2 : 1;

        if (num >= 1e9) return prefix + (num / 1e9).toFixed(decimalPlaces).replace(/\.0+$/, '') + 'B';
        if (num >= 1e6) return prefix + (num / 1e6).toFixed(decimalPlaces).replace(/\.0+$/, '') + 'M';
        if (num >= 1e3) return prefix + (num / 1e3).toFixed(decimalPlaces).replace(/\.0+$/, '') + 'K';
        
        return prefix + num.toLocaleString('pt-BR', { minimumFractionDigits: currency ? 2 : 0, maximumFractionDigits: currency ? 2 : 0 });
    },

    animateCounters: function() {
        document.querySelectorAll('.stat-value').forEach(element => {
            // ... (Animation logic) ...
        });
    },

    // *********************************
    // ** EMPLOYEE PERFORMANCE CHARTS **
    // *********************************
    EmployeePerformanceCharts: class {
        constructor(options = {}) {
            this.colors = RoarCharts.colors;
            this.defaults = {
                fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                gridColor: 'rgba(255, 255, 255, 0.05)',
                animationDuration: 1000
            };
            this.options = {...this.defaults, ...options};
        }

        initDashboardCharts() {
            const employeeComparisonEl = document.getElementById('employeeComparisonChart');
            if (employeeComparisonEl) {
                this.renderEmployeeComparisonChart(employeeComparisonEl);
            }
            document.querySelectorAll('.employee-performance-chart').forEach(chartEl => {
                const chartType = chartEl.dataset.chartType;
                const employeeId = chartEl.dataset.employeeId;
                if (chartType === 'contacts') this.renderEmployeeContactsChart(chartEl, employeeId);
                else if (chartType === 'success-rate') this.renderEmployeeSuccessRateChart(chartEl, employeeId);
                else if (chartType === 'conversion') this.renderEmployeeConversionChart(chartEl, employeeId);
            });
        }

        renderEmployeeComparisonChart(chartElement) {
            try {
                const employeeData = JSON.parse(chartElement.dataset.employees);
                const labels = employeeData.map(e => e.name);
                const contactsData = employeeData.map(e => e.contactCount);
                const successRateData = employeeData.map(e => e.successRate);
                const convertedLeadsData = employeeData.map(e => e.convertedLeads);
                new Chart(chartElement, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Contatos',
                            data: contactsData,
                            backgroundColor: this.colors.gold,
                        }, {
                            label: 'Taxa de Sucesso (%)',
                            data: successRateData,
                            backgroundColor: this.colors.green,
                        }, {
                            label: 'Leads Convertidos',
                            data: convertedLeadsData,
                            backgroundColor: this.colors.blue,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: { y: { beginAtZero: true } },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: (context) => `${context.dataset.label || ''}: ${context.parsed.y}${context.dataset.label.includes('Taxa') ? '%' : ''}`
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error rendering employee comparison chart:', error);
            }
        }

        renderEmployeeContactsChart(chartElement, employeeId) {
            const employeeIdNum = parseInt(employeeId, 10);
            if (isNaN(employeeIdNum)) return;

            const chartData = JSON.parse(chartElement.dataset.chartData || '[]');
            const filteredData = chartData.filter(entry => entry.employeeId === employeeIdNum);

            const labels = filteredData.map(e => e.month);
            const contactsData = filteredData.map(e => e.contactCount);

            new Chart(chartElement, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Contatos',
                        data: contactsData,
                        backgroundColor: this.colors.gold,
                        borderColor: this.colors.goldDark,
                        borderWidth: 2,
                        fill: true,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'month',
                                tooltipFormat: 'MMM YYYY',
                                displayFormats: {
                                    month: 'MMM YYYY'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Mês',
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 14,
                                    weight: 'bold'
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Contatos',
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 14,
                                    weight: 'bold'
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y;
                                    return `${label}: ${value}`;
                                }
                            }
                        },
                        legend: {
                            labels: {
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 12,
                                    weight: 'bold'
                                }
                            }
                        }
                    }
                });
        }

        renderEmployeeSuccessRateChart(chartElement, employeeId) {
            const employeeIdNum = parseInt(employeeId, 10);
            if (isNaN(employeeIdNum)) return;

            const chartData = JSON.parse(chartElement.dataset.chartData || '[]');
            const filteredData = chartData.filter(entry => entry.employeeId === employeeIdNum);

            const labels = filteredData.map(e => e.month);
            const successRateData = filteredData.map(e => e.successRate);

            new Chart(chartElement, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Taxa de Sucesso (%)',
                        data: successRateData,
                        backgroundColor: this.colors.green,
                        borderColor: this.colors.greenDark,
                        borderWidth: 2,
                        fill: true,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'month',
                                tooltipFormat: 'MMM YYYY',
                                displayFormats: {
                                    month: 'MMM YYYY'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Mês',
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 14,
                                    weight: 'bold'
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Taxa de Sucesso (%)',
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 14,
                                    weight: 'bold'
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y;
                                    return `${label}: ${value}%`;
                                }
                            }
                        },
                        legend: {
                            labels: {
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 12,
                                    weight: 'bold'
                                }
                            }
                        }
                    }
                });
        }

        renderEmployeeConversionChart(chartElement, employeeId) {
            const employeeIdNum = parseInt(employeeId, 10);
            if (isNaN(employeeIdNum)) return;

            const chartData = JSON.parse(chartElement.dataset.chartData || '[]');
            const filteredData = chartData.filter(entry => entry.employeeId === employeeIdNum);

            const labels = filteredData.map(e => e.month);
            const conversionData = filteredData.map(e => e.conversionRate);

            new Chart(chartElement, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Taxa de Conversão (%)',
                        data: conversionData,
                        backgroundColor: this.colors.blue,
                        borderColor: this.colors.blueDark,
                        borderWidth: 2,
                        fill: true,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'month',
                                tooltipFormat: 'MMM YYYY',
                                displayFormats: {
                                    month: 'MMM YYYY'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Mês',
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 14,
                                    weight: 'bold'
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Taxa de Conversão (%)',
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 14,
                                    weight: 'bold'
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y;
                                    return `${label}: ${value}%`;
                                }
                            }
                        },
                        legend: {
                            labels: {
                                color: '#ffffff',
                                font: {
                                    family: this.options.fontFamily,
                                    size: 12,
                                    weight: 'bold'
                                }
                            }
                        }
                    }
                });
        }
        
        renderEmployeeDetailsCharts(employeeData) {
            // ... (Implementation from employee-performance.js)
        }
    }
};

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    RoarCharts.initializeGlobalConfig();
    RoarCharts.registerGaugeChart();
    RoarCharts.animateCounters();

    if (document.querySelector('.employee-performance-chart, #employeeComparisonChart')) {
        const performanceCharts = new RoarCharts.EmployeePerformanceCharts();
        performanceCharts.initDashboardCharts();
    }
});
