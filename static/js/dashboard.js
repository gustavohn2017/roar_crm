
/**
 * Arquivo principal para funcionalidades do dashboard, incluindo diagnóstico e recuperação.
 */

// Namespace para o dashboard para evitar conflitos
const dashboard = {
    // Função para recuperar e exibir a lista de leads via AJAX
    fetchAndDisplayLeads: function() {
        const contentBody = document.getElementById('contentBody');
        if (!contentBody) {
            console.error("Elemento 'contentBody' não encontrado.");
            return;
        }

        // Mostrar indicador de carregamento
        contentBody.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Carregando lista de leads...</p>
            </div>
        `;
        
        // Atualizar cabeçalho
        if (typeof updateContentHeader === 'function') {
            updateContentHeader('Lista de Leads', 'Visualize e gerencie todos os seus leads');
        }
        
        // Fazer requisição AJAX usando fetch
        fetch('/leads/api/lista/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.renderLeadsTable(data);
            })
            .catch(error => {
                contentBody.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle"></i>
                        <strong>Erro ao carregar leads:</strong> ${error.message || 'Não foi possível carregar os dados.'}
                    </div>
                    <button class="btn btn-primary" onclick="dashboard.fetchAndDisplayLeads()">
                        <i class="bi bi-arrow-clockwise"></i> Tentar novamente
                    </button>
                    <a href="/leads/lista/" class="btn btn-secondary ms-2">
                        <i class="bi bi-box-arrow-up-right"></i> Abrir em nova página
                    </a>
                `;
            });
    },

    // Função para renderizar a tabela de leads
    renderLeadsTable: function(leads) {
        const contentBody = document.getElementById('contentBody');
        if (!contentBody) {
            console.error("Elemento 'contentBody' não encontrado.");
            return;
        }

        if (!leads || !Array.isArray(leads) || leads.length === 0) {
            contentBody.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    <strong>Nenhum lead encontrado.</strong>
                </div>
                <button class="btn btn-primary" onclick="openQuickLeadModal()">
                    <i class="bi bi-person-plus"></i> Cadastrar Novo Lead
                </button>
            `;
            return;
        }
        
        try {
            // Construir HTML da tabela
            let html = `
                <div class="mb-3 d-flex justify-content-between align-items-center">
                    <div class="input-group" style="max-width: 300px;">
                        <input type="text" id="searchLeads" class="form-control" placeholder="Buscar leads...">
                        <button class="btn btn-outline-secondary" type="button" id="btnSearchLeads">
                            <i class="bi bi-search"></i>
                        </button>
                    </div>
                    <div>
                        <span class="text-light me-2">Total: <strong>${leads.length}</strong> leads</span>
                        <button class="btn btn-primary" onclick="openQuickLeadModal()">
                            <i class="bi bi-person-plus"></i> Novo Lead
                        </button>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-striped table-dark table-hover">
                        <thead>
                            <tr>
                                <th>Nome</th>
                                <th>Telefone</th>
                                <th>Status</th>
                                <th>Interesse</th>
                                <th>Data de Criação</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            leads.forEach(lead => {
                if (!lead || typeof lead !== 'object') {
                    console.error('Lead inválido:', lead);
                    return;
                }
                
                const statusClass = this.getStatusClass(lead.status);
                const interestClass = this.getInterestClass(lead.interesse);
                const leadNome = lead.nome || 'Nome não informado';
                const leadTelefone = lead.telefone || 'Não informado';
                const leadStatus = lead.status || 'Status não definido';
                const leadInteresse = lead.interesse || 'Não informado';
                const leadData = new Date(lead.data_criacao).toLocaleDateString('pt-BR');

                html += `
                    <tr>
                        <td>${leadNome}</td>
                        <td>${leadTelefone}</td>
                        <td><span class="badge ${statusClass}">${leadStatus}</span></td>
                        <td><span class="badge ${interestClass}">${leadInteresse}</span></td>
                        <td>${leadData}</td>
                        <td>
                            <a href="/leads/${lead.id}/" class="btn btn-sm btn-info" title="Ver Detalhes">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="/leads/${lead.id}/edit/" class="btn btn-sm btn-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                        </td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
            
            contentBody.innerHTML = html;
            
            // Adicionar listener para busca
            document.getElementById('btnSearchLeads').addEventListener('click', () => {
                const searchTerm = document.getElementById('searchLeads').value.toLowerCase();
                const filteredLeads = leads.filter(lead => 
                    (lead.nome || '').toLowerCase().includes(searchTerm) ||
                    (lead.telefone || '').toLowerCase().includes(searchTerm)
                );
                this.renderLeadsTable(filteredLeads);
            });

        } catch (e) {
            console.error("Erro ao renderizar tabela de leads:", e);
            contentBody.innerHTML = `<div class="alert alert-danger">Ocorreu um erro inesperado ao exibir os leads.</div>`;
        }
    },

    // Funções auxiliares para classes de status e interesse
    getStatusClass: function(status) {
        switch (status) {
            case 'Novo': return 'bg-primary';
            case 'Em Atendimento': return 'bg-info';
            case 'Qualificado': return 'bg-success';
            case 'Não Qualificado': return 'bg-danger';
            case 'Vendido': return 'bg-warning text-dark';
            default: return 'bg-secondary';
        }
    },

    getInterestClass: function(interesse) {
        if (!interesse) return 'bg-dark';
        if (interesse.includes('Consórcio')) return 'bg-info';
        if (interesse.includes('Crédito')) return 'bg-success';
        return 'bg-secondary';
    },

    // Função de diagnóstico
    diagnosticar: function() {
        console.log('=== DIAGNÓSTICO DO DASHBOARD ===');
        
        const funcoesEssenciais = [
            'loadTool', 'showLoading', 'updateContentHeader', 'executeScripts',
            'dashboard.fetchAndDisplayLeads', 'dashboard.renderLeadsTable'
        ];
        
        funcoesEssenciais.forEach(funcName => {
            // Para funções aninhadas no objeto dashboard
            const func = funcName.split('.').reduce((o, i) => o ? o[i] : undefined, window);
            if (typeof func === 'function') {
                console.log(`✓ Função ${funcName} encontrada`);
            } else {
                console.error(`✗ Função ${funcName} NÃO encontrada`);
            }
        });
        
        const elementosEssenciais = ['contentBody', 'contentHeader', 'contentTitle', 'contentDescription'];
        
        elementosEssenciais.forEach(id => {
            if (document.getElementById(id)) {
                console.log(`✓ Elemento #${id} encontrado`);
            } else {
                console.error(`✗ Elemento #${id} NÃO encontrado`);
            }
        });
        
        if (typeof $ === 'function') {
            console.log('✓ jQuery disponível (versão ' + $.fn.jquery + ')');
        } else {
            console.error('✗ jQuery NÃO disponível');
        }
        
        fetch('/leads/api/lista/')
            .then(response => {
                if (response.ok) {
                    console.log('✓ API de leads respondendo corretamente');
                } else {
                    console.error(`✗ API de leads retornou status ${response.status}`);
                }
            })
            .catch(error => console.error('✗ Erro ao acessar API de leads:', error));
        
        console.log('=== FIM DO DIAGNÓSTICO ===');
    }
};

// Expor a função de diagnóstico globalmente se necessário, ou chamar em um evento específico
// window.runDashboardDiagnosis = dashboard.diagnosticar;
