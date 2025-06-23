/**
 * Gauge Chart plugin for Chart.js
 * Adiciona suporte para gráficos do tipo gauge no Chart.js
 */

Chart.controllers.gauge = Chart.controllers.doughnut.extend({
    initialize: function() {
        Chart.controllers.doughnut.prototype.initialize.apply(this, arguments);
    },
    
    draw: function() {
        Chart.controllers.doughnut.prototype.draw.apply(this, arguments);
        
        const chart = this.chart;
        const ctx = chart.ctx;
        const value = chart.config.data.datasets[0].value;
        
        // Se o valor não estiver definido, não renderiza a agulha
        if (value === undefined) {
            return;
        }
        
        const chartArea = chart.chartArea;
        const centerX = (chartArea.left + chartArea.right) / 2;
        const centerY = (chartArea.top + chartArea.bottom) / 2;
        
        // Configurações da agulha
        const needleConfig = chart.options.needle || {};
        const radiusPercentage = needleConfig.radiusPercentage || 2;
        const widthPercentage = needleConfig.widthPercentage || 3;
        const lengthPercentage = needleConfig.lengthPercentage || 80;
        const color = needleConfig.color || 'rgba(0, 0, 0, 0.75)';
        
        const outerRadius = Math.min(chart.chartArea.right - chart.chartArea.left, chart.chartArea.bottom - chart.chartArea.top) / 2;
        const radius = outerRadius * (radiusPercentage / 100);
        const width = outerRadius * (widthPercentage / 100);
        const length = outerRadius * (lengthPercentage / 100);
        
        // Converter o valor para ângulo em radianos (considerando que o valor máximo é 100)
        const valueMax = chart.options.valueMax || 100;
        const angle = Math.PI * (1 - (value / valueMax));
        
        // Desenhar a agulha
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(angle);
        
        // Base circular da agulha
        ctx.beginPath();
        ctx.arc(0, 0, radius, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        
        // Linha da agulha
        ctx.beginPath();
        ctx.moveTo(0, -width / 2);
        ctx.lineTo(length, 0);
        ctx.lineTo(0, width / 2);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        
        ctx.restore();
        
        // Adicionar o valor no centro se configurado
        const valueLabel = chart.options.valueLabel || {};
        if (valueLabel.display) {
            const fontSize = valueLabel.fontSize || 16;
            const fontStyle = valueLabel.fontStyle || 'bold';
            const fontColor = valueLabel.color || '#000';
            const bottomMarginPercentage = valueLabel.bottomMarginPercentage || 0;
            const formatter = valueLabel.formatter || function(val) { return val; };
            
            // Centralizar o texto
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.font = `${fontStyle} ${fontSize}px Arial`;
            ctx.fillStyle = fontColor;
            
            // Ajustar a posição vertical com base na margem inferior
            const bottomMargin = outerRadius * (bottomMarginPercentage / 100);
            ctx.fillText(formatter(value), centerX, centerY + bottomMargin);
        }
    }
});

// Registro do tipo de gráfico gauge
Chart.defaults.gauge = Chart.helpers.clone(Chart.defaults.doughnut);

// Extensão do método getDatasetMeta para incluir o controlador gauge
const originalGetDatasetMeta = Chart.prototype.getDatasetMeta;
Chart.prototype.getDatasetMeta = function(datasetIndex) {
    const meta = originalGetDatasetMeta.apply(this, arguments);
    if (meta.type === 'gauge') {
        meta.controller = meta.controller || new Chart.controllers.gauge(this, datasetIndex);
    }
    return meta;
};
