/**
 * Arquivo de diagnóstico para problemas de carregamento no dashboard
 */

// Verifica se todas as funções essenciais estão registradas
function diagnosticarDashboard() {
    console.log('=== DIAGNÓSTICO DO DASHBOARD ===');
    
    // Verificar funções essenciais
    const funcoesEssenciais = [
        'loadTool', 
        'showLoading', 
        'updateContentHeader', 
        'executeScripts',
        'fetchAndDisplayLeads',
        'renderLeadsTable'
    ];
    
    funcoesEssenciais.forEach(func => {
        if (typeof window[func] === 'function') {
            console.log(`✓ Função ${func} encontrada`);
        } else {
            console.error(`✗ Função ${func} NÃO encontrada`);
        }
    });
    
    // Verificar elementos da UI
    const elementosEssenciais = [
        'contentBody',
        'contentHeader',
        'contentTitle',
        'contentDescription'
    ];
    
    elementosEssenciais.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            console.log(`✓ Elemento #${id} encontrado`);
        } else {
            console.error(`✗ Elemento #${id} NÃO encontrado`);
        }
    });
    
    // Verificar se jQuery está disponível
    if (typeof $ === 'function') {
        console.log('✓ jQuery disponível (versão ' + $.fn.jquery + ')');
    } else {
        console.error('✗ jQuery NÃO disponível');
    }
    
    // Verificar conexão com a API de leads
    fetch('/leads/api/lista/')
        .then(response => {
            if (response.ok) {
                console.log('✓ API de leads respondendo corretamente');
                return response.json();
            } else {
                console.error(`✗ API de leads retornou status ${response.status}`);
                return response.text().then(text => {
                    try {
                        return JSON.parse(text);
                    } catch {
                        console.error('Resposta não é JSON válido:', text.substring(0, 100));
                        return null;
                    }
                });
            }
        })
        .then(data => {
            if (Array.isArray(data)) {
                console.log(`✓ API retornou ${data.length} leads`);
                if (data.length > 0) {
                    console.log('Exemplo do primeiro lead:', data[0]);
                }
            } else if (data) {
                console.error('✗ API não retornou um array:', data);
            }
        })
        .catch(error => {
            console.error('✗ Erro ao acessar API de leads:', error);
        });
    
    console.log('=== FIM DO DIAGNÓSTICO ===');
}

// Verificar todas as rotas importantes
function verificarRotas() {
    const rotas = [
        { nome: 'Lista de Leads', url: '/leads/lista/' },
        { nome: 'API de Leads', url: '/leads/api/lista/' },
        { nome: 'Calendário', url: '/vendedores/utils/calendario/' },
        { nome: 'Bloco de Notas', url: '/vendedores/utils/notas/' },
        { nome: 'Calculadoras', url: '/vendedores/utils/calculadoras/' },
        { nome: 'Funil de Vendas', url: '/vendedores/utils/funnel/' },
        { nome: 'Histórico de Contatos', url: '/vendedores/historico/' }
    ];
    
    console.log('=== VERIFICAÇÃO DE ROTAS ===');
    
    rotas.forEach(rota => {
        fetch(rota.url)
            .then(response => {
                if (response.ok) {
                    console.log(`✓ ${rota.nome}: OK (${response.status})`);
                } else {
                    console.error(`✗ ${rota.nome}: FALHOU (${response.status})`);
                }
            })
            .catch(error => {
                console.error(`✗ ${rota.nome}: ERRO (${error.message})`);
            });
    });
}

// Corrigir problemas comuns
function repararDashboard() {
    console.log('Tentando reparar problemas comuns do dashboard...');
    
    // Garantir que o contentBody existe
    if (!document.getElementById('contentBody')) {
        console.log('Criando elemento contentBody que está faltando...');
        const contentArea = document.querySelector('.content-area') || document.querySelector('main');
        if (contentArea) {
            const contentBody = document.createElement('div');
            contentBody.id = 'contentBody';
            contentBody.className = 'content-body';
            contentArea.appendChild(contentBody);
            console.log('✓ Elemento contentBody criado com sucesso');
        } else {
            console.error('✗ Não foi possível encontrar o container para criar contentBody');
        }
    }
    
    // Restaurar funções essenciais
    if (typeof loadTool !== 'function') {
        console.log('Restaurando função loadTool...');
        window.loadTool = function(toolId, toolName, toolUrl) {
            console.log(`Carregando ferramenta: ${toolName} de ${toolUrl}`);
            if (toolId === 'leads') {
                fetchAndDisplayLeads();
                return;
            }
            
            // Para outras ferramentas, redirecionar
            window.location.href = toolUrl;
        };
    }
    
    console.log('Reparos concluídos, recarregue a página para aplicar as alterações');
}

// Exportar funções para uso global
window.diagnosticarDashboard = diagnosticarDashboard;
window.verificarRotas = verificarRotas;
window.repararDashboard = repararDashboard;

// Mensagem no console para o usuário
console.log(`
=========================================
DIAGNÓSTICO DO DASHBOARD DISPONÍVEL:
Para resolver problemas, digite no console:
- diagnosticarDashboard() - Para identificar problemas
- verificarRotas() - Para verificar rotas do sistema
- repararDashboard() - Para tentar reparar problemas comuns
=========================================
`);
