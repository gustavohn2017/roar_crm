/**
 * Funções de formatação para valores monetários e numéricos
 * Converte valores grandes em formato legível (ex: 1.2M, 500K)
 */

/**
 * Função aprimorada para formatação de valores grandes em formato legível
 * Converte valores para formato K (mil), M (milhão) ou B (bilhão) de acordo com o tamanho
 * 
 * @param {string|number} value - Valor a ser formatado 
 * @param {boolean} currency - Se deve ser formatado como moeda (R$)
 * @param {boolean} precise - Se deve manter mais precisão nos decimais
 * @returns {string} Valor formatado
 */
function formatLargeNumber(value, currency = false, precise = false) {
    // Tratar casos de valores vazios ou inválidos
    if (!value || isNaN(value)) return currency ? 'R$ 0' : '0';
    
    // Converter o valor para número, lidando com formatos de moeda brasileira
    const num = parseFloat(
        value.toString()
             .replace(/[^\d.,]/g, '') // Remove caracteres não numéricos
             .replace(/\./g, '')      // Remove pontos de milhares
             .replace(',', '.')       // Converte vírgula decimal para ponto
    );
    
    // Prefixo de moeda para valores em reais
    const prefix = currency ? 'R$ ' : '';
    
    // Determinar casas decimais baseado na precisão solicitada
    const decimalPlaces = precise ? 2 : 1;
    
    // Formatar valores grandes de forma mais legível
    if (num >= 1000000000) {
        // Bilhões
        return prefix + (num / 1000000000).toFixed(decimalPlaces).replace(/\.0+$/, '') + 'B';
    } else if (num >= 1000000) {
        // Milhões
        return prefix + (num / 1000000).toFixed(decimalPlaces).replace(/\.0+$/, '') + 'M';
    } else if (num >= 1000) {
        // Milhares
        return prefix + (num / 1000).toFixed(decimalPlaces).replace(/\.0+$/, '') + 'K';
    } else {
        // Valores menores que mil - usar formatação de moeda brasileira quando apropriado
        return prefix + num.toLocaleString('pt-BR', {
            minimumFractionDigits: currency ? 2 : 0,
            maximumFractionDigits: currency ? 2 : 0
        });
    }
}

function formatPercentage(value) {
    if (!value || isNaN(value)) return '0%';
    const num = parseFloat(value);
    return num.toFixed(1) + '%';
}

/**
 * Aplicar formatação aos cards de estatísticas
 */
function formatStatCards() {
    document.querySelectorAll('.stat-card').forEach(card => {
        const valueElement = card.querySelector('.stat-value');
        const labelElement = card.querySelector('.stat-label');
        
        if (!valueElement || !labelElement) return;
        
        const label = labelElement.textContent.toLowerCase();
        const originalValue = valueElement.textContent;
        
        // Adicionar tooltip com valor original
        valueElement.title = `Valor exato: ${originalValue}`;
        
        if (label.includes('conversão') || label.includes('%')) {
            // Já está formatado como porcentagem
            return;
        } else if (label.includes('valor') || label.includes('receita') || originalValue.includes('R$')) {
            // Formatar valores monetários
            const cleanValue = originalValue.replace(/[^\d,]/g, '').replace(',', '.');
            valueElement.textContent = formatLargeNumber(cleanValue, true);
        } else if (label.includes('leads') || label.includes('total')) {
            // Formatar números simples
            const cleanValue = originalValue.replace(/[^\d]/g, '');
            valueElement.textContent = formatLargeNumber(cleanValue, false);
        }
    });
}

/**
 * Animar os valores dos cards com contador
 */
function animateCounters() {
    document.querySelectorAll('.stat-value').forEach(element => {
        const finalText = element.textContent;
        const isPercentage = finalText.includes('%');
        const isCurrency = finalText.includes('R$');
        
        // Extrair número para animação
        let finalValue = parseFloat(finalText.replace(/[^\d.,]/g, '').replace(',', '.')) || 0;
        
        let currentValue = 0;
        const increment = finalValue / 30; // 30 frames de animação
        const duration = 1500; // 1.5 segundos
        const frameRate = duration / 30;
        
        element.textContent = isCurrency ? 'R$ 0' : '0' + (isPercentage ? '%' : '');
        
        const counter = setInterval(() => {
            currentValue += increment;
            
            if (currentValue >= finalValue) {
                element.textContent = finalText;
                clearInterval(counter);
            } else {
                if (isCurrency) {
                    element.textContent = formatLargeNumber(currentValue, true);
                } else if (isPercentage) {
                    element.textContent = currentValue.toFixed(1) + '%';
                } else {
                    element.textContent = formatLargeNumber(currentValue, false);
                }
            }
        }, frameRate);
    });
}

/**
 * Anima um contador do valor inicial até o valor final
 * 
 * @param {HTMLElement} element - Elemento que receberá o valor animado
 * @param {number} start - Valor inicial 
 * @param {number} end - Valor final
 * @param {number} duration - Duração da animação em ms
 * @param {Object} options - Opções de formatação
 */
function animateValue(element, start, end, duration, options = {}) {
    // Valores padrão para opções
    const {
        isCurrency = false,
        isPercentage = false,
        useK = false,
        useExactFormat = false
    } = options;
    
    // Guardar valor original para tooltip
    const originalFormatted = element.textContent;
    element.setAttribute('title', `Valor exato: ${originalFormatted}`);
    
    // Tempo de início da animação
    const startTime = performance.now();
    
    // Função para atualizar o contador a cada frame
    function updateCounter(currentTime) {
        // Calcular progresso da animação
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Função de easing para animação mais natural
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = start + (end - start) * easeOutQuart;
        
        // Formatar valor de acordo com o tipo
        let displayValue;
        
        if (useExactFormat) {
            // Usar formatação exata do valor original
            const percentage = current / end;
            displayValue = originalFormatted;
        } else if (isCurrency) {
            // Formatar como moeda
            displayValue = formatLargeNumber(current, true, false);
        } else if (isPercentage) {
            // Formatar como porcentagem
            displayValue = current.toFixed(1) + '%';
        } else if (useK && end > 1000) {
            // Usar formato K para valores maiores que 1000
            displayValue = formatLargeNumber(current, false, false);
        } else {
            // Formatar como número inteiro
            displayValue = Math.floor(current).toLocaleString('pt-BR');
        }
        
        // Atualizar o elemento
        element.textContent = displayValue;
        
        // Continuar a animação se não atingiu o fim
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            // Garantir que ao final da animação o valor exato seja exibido
            if (!useExactFormat) {
                if (isCurrency) {
                    element.textContent = formatLargeNumber(end, true, false);
                } else if (isPercentage) {
                    element.textContent = end.toFixed(1) + '%';
                } else if (useK && end > 1000) {
                    element.textContent = formatLargeNumber(end, false, false);
                } else {
                    element.textContent = Math.floor(end).toLocaleString('pt-BR');
                }
            }
            
            // Adicionar classe para indicar fim da animação
            element.classList.add('animated');
        }
    }
    
    // Iniciar animação
    requestAnimationFrame(updateCounter);
}

/**
 * Adicionar indicadores de tendência
 */
function addTrendIndicators() {
    // Simulação de dados de tendência (em produção, viria do backend)
    const trends = {
        'leads totais': { direction: 'up', percentage: 12 },
        'taxa de conversão': { direction: 'down', percentage: 3 },
        'valor de interesse': { direction: 'up', percentage: 8 },
        'valor fechado': { direction: 'up', percentage: 25 }
    };
    
    document.querySelectorAll('.stat-card').forEach(card => {
        const label = card.querySelector('.stat-label').textContent.toLowerCase();
        const trend = trends[label];
        
        if (trend && !card.querySelector('.trend-indicator')) {
            const trendElement = document.createElement('div');
            trendElement.className = `trend-indicator trend-${trend.direction}`;
            trendElement.innerHTML = `
                <i class="bi bi-arrow-${trend.direction === 'up' ? 'up' : 'down'}-short"></i>
                ${trend.percentage}%
            `;
            
            card.querySelector('.stat-info').appendChild(trendElement);
        }
    });
}

/**
 * Inicialização quando o DOM estiver carregado
 * Aplica efeitos visuais e formatação aos cartões de estatísticas
 */
document.addEventListener('DOMContentLoaded', function() {
    // Iniciar com efeito de carregamento (skeleton)
    document.querySelectorAll('.stat-value').forEach(el => {
        el.classList.add('loading');
    });
    
    // Sequência de animações com timing adequado
    setTimeout(() => {
        // Remover estado de carregamento
        document.querySelectorAll('.stat-value').forEach(el => {
            el.classList.remove('loading');
        });
        
        // Primeiro, formatar os valores para exibição
        formatStatCards();
        
        // Em seguida, iniciar animações de contagem
        setTimeout(() => {
            const statValues = document.querySelectorAll('.stat-value.counter');
            
            statValues.forEach((el, index) => {
                // Extrair valor original do atributo data
                const rawValue = el.getAttribute('data-value');
                if (!rawValue) return;
                
                // Verificar tipo de valor
                const isCurrency = el.classList.contains('currency');
                const isPercentage = el.classList.contains('percentage');
                
                // Parsear valor de acordo com o tipo
                let numValue;
                if (isPercentage) {
                    numValue = parseFloat(rawValue);
                } else if (isCurrency) {
                    numValue = parseFloat(
                        rawValue.toString()
                            .replace(/[^\d.,]/g, '')
                            .replace(/\./g, '')
                            .replace(',', '.')
                    );
                } else {
                    numValue = parseInt(rawValue.replace(/\D/g, ''));
                }
                
                // Valor inválido, pular animação
                if (isNaN(numValue)) return;
                
                // Animação com tempo escalonado para efeito cascata
                setTimeout(() => {
                    animateValue(el, 0, numValue, 1500, {
                        isCurrency,
                        isPercentage,
                        useK: numValue >= 1000,
                        useExactFormat: el.hasAttribute('data-exact-format')
                    });
                }, index * 150);
            });
        }, 200);
        
        // Adicionar indicadores de tendência após formatação
        setTimeout(addTrendIndicators, 600);
        
        // Por último, destacar o valor mais significativo
        setTimeout(() => {
            highlightSignificantValue();
        }, 1200);
    }, 600);
    
    // Adicionar eventos de hover para detalhes
    addCardInteractions();
});

/**
 * Destaca o valor mais significativo entre os cartões de estatísticas
 */
function highlightSignificantValue() {
    const valueElements = document.querySelectorAll('.stat-value');
    let maxValue = 0;
    let maxElement = null;
    
    // Encontrar o maior valor monetário
    valueElements.forEach(el => {
        if (el.textContent.includes('R$') && el.parentNode.textContent.toLowerCase().includes('fechado')) {
            // Extrair o valor numérico ignorando formatação
            let valueText = el.textContent;
            
            // Detectar valores abreviados (K, M, B)
            let multiplier = 1;
            if (valueText.includes('K')) multiplier = 1000;
            if (valueText.includes('M')) multiplier = 1000000;
            if (valueText.includes('B')) multiplier = 1000000000;
            
            // Remover sufixos e extrair valor base
            const baseValue = parseFloat(
                valueText
                    .replace(/[^\d.,]/g, '')
                    .replace(/\./g, '')
                    .replace(',', '.')
            ) * multiplier;
            
            if (baseValue > maxValue) {
                maxValue = baseValue;
                maxElement = el;
            }
        }
    });
    
    // Adicionar efeito de destaque
    if (maxElement) {
        maxElement.classList.add('highlight');
        
        // Adicionar dados contextuais
        const cardElement = maxElement.closest('.stat-card');
        if (cardElement) {
            cardElement.setAttribute('data-highlight', 'true');
            
            // Adicionar badge contextual se valor for significativo
            if (maxValue > 100000) {
                const badgeElement = document.createElement('div');
                badgeElement.className = 'highlight-badge';
                badgeElement.innerHTML = '<i class="bi bi-star-fill"></i>';
                badgeElement.title = 'Valor Destacado';
                cardElement.appendChild(badgeElement);
            }
        }
    }
}

/**
 * Adiciona interações aos cartões de estatísticas
 */
function addCardInteractions() {
    // Adicionar tooltip avançado em hover
    document.querySelectorAll('.stat-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Encontrar elementos dentro do card
            const valueEl = this.querySelector('.stat-value');
            const labelEl = this.querySelector('.stat-label');
            
            if (!valueEl || !valueEl.hasAttribute('title')) return;
            
            // Criar tooltip avançado se ainda não existe
            if (!this.querySelector('.advanced-tooltip')) {
                const tooltip = document.createElement('div');
                tooltip.className = 'advanced-tooltip';
                tooltip.textContent = valueEl.getAttribute('title');
                tooltip.style.position = 'absolute';
                tooltip.style.bottom = '100%';
                tooltip.style.left = '50%';
                tooltip.style.transform = 'translateX(-50%)';
                tooltip.style.padding = '0.5rem';
                tooltip.style.background = 'rgba(0,0,0,0.8)';
                tooltip.style.borderRadius = '4px';
                tooltip.style.fontSize = '0.7rem';
                tooltip.style.zIndex = '10';
                tooltip.style.opacity = '0';
                tooltip.style.transition = 'opacity 0.3s';
                
                this.style.position = 'relative';
                this.appendChild(tooltip);
                
                // Mostrar tooltip com delay
                setTimeout(() => {
                    tooltip.style.opacity = '1';
                }, 300);
            }
        });
        
        // Remover tooltip ao sair
        card.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('.advanced-tooltip');
            if (tooltip) {
                tooltip.style.opacity = '0';
                setTimeout(() => tooltip.remove(), 300);
            }
        });
    });
}
