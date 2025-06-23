/**
 * Test Script for Sales Funnel Verification
 * This script helps to verify if the Sales Funnel components are loaded and working correctly
 * Version: 1.0
 * Date: 13/06/2025
 */

// Execute tests when page is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Give some time for all components to load
    setTimeout(runFunnelTests, 1000);
});

/**
 * Main function that runs all tests
 */
function runFunnelTests() {
    console.group('🧪 TESTES DO FUNIL DE VENDAS');
    
    // Test if CSS loaded correctly
    testCSSLoading();
    
    // Test if components are present
    testComponentsPresence();
    
    // Test if funnel segments match kanban columns
    testFunnelKanbanMatch();
    
    // Test if all scripts are loaded
    testScriptsLoaded();
    
    // Test browser compatibility
    testBrowserCompatibility();
    
    console.groupEnd();
    
    // Show results on page for admin users
    if (document.body.classList.contains('admin-user')) {
        showTestResultsOnPage();
    }
}

/**
 * Test if CSS is loaded correctly
 */
function testCSSLoading() {
    console.group('1. Teste de carregamento CSS');
    
    const style = getComputedStyle(document.documentElement);
    const testLoaded = style.getPropertyValue('--test-loaded').trim();
    const funnelBg = style.getPropertyValue('--funnel-bg').trim();
    
    if (testLoaded === '1') {
        console.log('✅ Variável de teste CSS detectada');
    } else {
        console.error('❌ Variável de teste CSS não encontrada');
    }
    
    if (funnelBg && funnelBg !== '') {
        console.log('✅ Variáveis de cor do funil detectadas');
    } else {
        console.error('❌ Variáveis de cor do funil não encontradas');
    }
    
    // Check if emergency styles were applied
    if (document.body.classList.contains('funnel-css-loaded')) {
        console.log('✅ CSS do funil carregado normalmente');
    } else {
        console.warn('⚠️ CSS do funil pode não ter carregado corretamente - verificando estilos de emergência');
        
        const emergencyStyles = document.querySelector('style[data-emergency="true"]');
        if (emergencyStyles) {
            console.warn('⚠️ Estilos de emergência foram aplicados');
        }
    }
    
    console.groupEnd();
}

/**
 * Test if all components are present in the page
 */
function testComponentsPresence() {
    console.group('2. Teste de presença dos componentes');
    
    // Test funnel visualization
    const funnelViz = document.querySelector('.funnel-visualization');
    if (funnelViz) {
        console.log('✅ Visualização do funil encontrada');
    } else {
        console.error('❌ Visualização do funil não encontrada');
    }
    
    // Test kanban board
    const kanbanBoard = document.querySelector('.kanban-board');
    if (kanbanBoard) {
        console.log('✅ Quadro kanban encontrado');
    } else {
        console.error('❌ Quadro kanban não encontrado');
    }
    
    // Test stats cards
    const statsCards = document.querySelectorAll('.stat-card');
    if (statsCards.length > 0) {
        console.log(`✅ ${statsCards.length} cards de estatísticas encontrados`);
    } else {
        console.error('❌ Cards de estatísticas não encontrados');
    }
    
    // Test kanban columns
    const kanbanColumns = document.querySelectorAll('.kanban-column');
    if (kanbanColumns.length > 0) {
        console.log(`✅ ${kanbanColumns.length} colunas kanban encontradas`);
        
        // Test if all expected columns are present
        const expectedColumns = ['new', 'contacted', 'qualified', 'negotiation', 'closed', 'lost'];
        const foundColumns = Array.from(kanbanColumns).map(col => {
            // Extract column type from class or ID
            const idMatch = col.id.match(/column-(.*)/);
            return idMatch ? idMatch[1] : null;
        }).filter(Boolean);
        
        const missingColumns = expectedColumns.filter(col => !foundColumns.includes(col));
        
        if (missingColumns.length === 0) {
            console.log('✅ Todas as colunas esperadas estão presentes');
        } else {
            console.warn(`⚠️ Algumas colunas estão faltando: ${missingColumns.join(', ')}`);
        }
    } else {
        console.error('❌ Colunas kanban não encontradas');
    }
    
    console.groupEnd();
}

/**
 * Test if funnel segments match kanban columns in count
 */
function testFunnelKanbanMatch() {
    console.group('3. Teste de correspondência funnel-kanban');
    
    const segments = document.querySelectorAll('.funnel-segment');
    const columns = document.querySelectorAll('.kanban-column');
    
    if (segments.length === columns.length) {
        console.log(`✅ Número de segmentos (${segments.length}) corresponde ao número de colunas (${columns.length})`);
    } else {
        console.error(`❌ Número de segmentos (${segments.length}) não corresponde ao número de colunas (${columns.length})`);
    }
    
    // Test if counts match
    let allMatch = true;
    segments.forEach((segment, index) => {
        if (columns[index]) {
            const segmentCount = segment.querySelector('.funnel-segment-count')?.textContent.trim();
            const columnCount = columns[index].querySelector('.kanban-column-count')?.textContent.trim();
            
            if (segmentCount === columnCount) {
                console.log(`✅ Contagem do segmento ${index+1} (${segmentCount}) corresponde à coluna`);
            } else {
                console.error(`❌ Contagem do segmento ${index+1} (${segmentCount}) não corresponde à coluna (${columnCount})`);
                allMatch = false;
            }
        }
    });
    
    if (allMatch) {
        console.log('✅ Todas as contagens correspondem entre segmentos e colunas');
    }
    
    console.groupEnd();
}

/**
 * Test if all required scripts are loaded
 */
function testScriptsLoaded() {
    console.group('4. Teste de carregamento de scripts');
    
    // Check if our scripts define specific functions
    if (typeof formatLargeNumber === 'function') {
        console.log('✅ stats-formatter.js carregado');
    } else {
        console.error('❌ stats-formatter.js não carregado ou não definiu funções esperadas');
    }
    
    if (typeof optimizeKanbanScrolling === 'function') {
        console.log('✅ funnel-optimizer.js carregado');
    } else {
        console.error('❌ funnel-optimizer.js não carregado ou não definiu funções esperadas');
    }
    
    console.groupEnd();
}

/**
 * Test browser compatibility
 */
function testBrowserCompatibility() {
    console.group('5. Teste de compatibilidade do navegador');
    
    // Check for CSS features
    const cssFeatures = {
        'CSS Variables': window.CSS && window.CSS.supports && window.CSS.supports('--test', '0'),
        'CSS Grid': window.CSS && window.CSS.supports && window.CSS.supports('display', 'grid'),
        'CSS Flexbox': window.CSS && window.CSS.supports && window.CSS.supports('display', 'flex'),
        'CSS Animations': window.CSS && window.CSS.supports && window.CSS.supports('animation', 'name'),
    };
    
    for (const [feature, supported] of Object.entries(cssFeatures)) {
        if (supported) {
            console.log(`✅ ${feature}: Suportado`);
        } else {
            console.warn(`⚠️ ${feature}: Não suportado - usando fallbacks`);
        }
    }
    
    // Check for JS features
    const jsFeatures = {
        'Intersection Observer': 'IntersectionObserver' in window,
        'Fetch API': 'fetch' in window,
        'Promise': 'Promise' in window,
        'LocalStorage': 'localStorage' in window,
    };
    
    for (const [feature, supported] of Object.entries(jsFeatures)) {
        if (supported) {
            console.log(`✅ ${feature}: Suportado`);
        } else {
            console.warn(`⚠️ ${feature}: Não suportado - usando fallbacks`);
        }
    }
    
    // Log user agent for reference
    console.log('📱 User Agent: ' + navigator.userAgent);
    
    console.groupEnd();
}

/**
 * Display test results on the page for admin users
 */
function showTestResultsOnPage() {
    // Create test results container
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'test-results-container';
    resultsContainer.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 12px;
        max-width: 300px;
        max-height: 400px;
        overflow-y: auto;
        z-index: 9999;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    `;
    
    // Add header
    const header = document.createElement('div');
    header.innerHTML = '<b>🧪 RESULTADOS DOS TESTES</b>';
    header.style.marginBottom = '10px';
    resultsContainer.appendChild(header);
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '×';
    closeButton.style.cssText = `
        position: absolute;
        top: 5px;
        right: 5px;
        background: none;
        border: none;
        color: white;
        font-size: 16px;
        cursor: pointer;
    `;
    closeButton.onclick = function() {
        resultsContainer.remove();
    };
    resultsContainer.appendChild(closeButton);
    
    // Capture console logs
    const logs = [];
    const originalConsoleLog = console.log;
    const originalConsoleError = console.error;
    const originalConsoleWarn = console.warn;
    
    function addLog(type, ...args) {
        logs.push({ type, message: args.join(' ') });
    }
    
    // Override console methods temporarily to capture test logs
    console.log = (...args) => {
        originalConsoleLog.apply(console, args);
        addLog('log', ...args);
    };
    
    console.error = (...args) => {
        originalConsoleError.apply(console, args);
        addLog('error', ...args);
    };
    
    console.warn = (...args) => {
        originalConsoleWarn.apply(console, args);
        addLog('warn', ...args);
    };
    
    // Re-run tests to capture logs
    runFunnelTests();
    
    // Restore console methods
    console.log = originalConsoleLog;
    console.error = originalConsoleError;
    console.warn = originalConsoleWarn;
    
    // Add logs to results container
    logs.forEach(log => {
        const logEntry = document.createElement('div');
        let icon = '';
        
        if (log.message.includes('✅')) icon = '✅';
        else if (log.message.includes('❌')) icon = '❌';
        else if (log.message.includes('⚠️')) icon = '⚠️';
        
        logEntry.innerHTML = log.message;
        
        switch (log.type) {
            case 'error':
                logEntry.style.color = '#ff5f5f';
                break;
            case 'warn':
                logEntry.style.color = '#ffbb00';
                break;
            default:
                if (log.message.includes('✅')) {
                    logEntry.style.color = '#4caf50';
                }
        }
        
        resultsContainer.appendChild(logEntry);
    });
    
    // Add to page
    document.body.appendChild(resultsContainer);
}

// Expose test function globally for manual testing
window.runFunnelTests = runFunnelTests;
