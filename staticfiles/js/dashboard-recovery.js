// Backup de funções para quando o carregamento dinâmico falhar

// Função para recuperar e exibir a lista de leads via AJAX
function fetchAndDisplayLeads() {
    // Mostrar indicador de carregamento
    document.getElementById('contentBody').innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Carregando lista de leads...</p>
        </div>
    `;
    
    // Atualizar cabeçalho
    updateContentHeader('Lista de Leads', 'Visualize e gerencie todos os seus leads');
    
    // Fazer requisição AJAX usando fetch ao invés de jQuery
    fetch('/leads/api/lista/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            renderLeadsTable(data);
        })
        .catch(error => {
            document.getElementById('contentBody').innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <strong>Erro ao carregar leads:</strong> ${error.message || 'Não foi possível carregar os dados.'}
                </div>
                <button class="btn btn-primary" onclick="fetchAndDisplayLeads()">
                    <i class="bi bi-arrow-clockwise"></i> Tentar novamente
                </button>
                <a href="/leads/lista/" class="btn btn-secondary ms-2">
                    <i class="bi bi-box-arrow-up-right"></i> Abrir em nova página
                </a>
            `;
        });
}

// Função para renderizar a tabela de leads
function renderLeadsTable(leads) {
    if (!leads || !Array.isArray(leads) || leads.length === 0) {
        document.getElementById('contentBody').innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i>
                <strong>Nenhum lead encontrado.</strong> Não há leads disponíveis no momento.
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
        
        // Adicionar linhas para cada lead
        leads.forEach(lead => {
            // Verificar se os campos necessários existem
            if (!lead || typeof lead !== 'object') {
                console.error('Lead inválido:', lead);
                return;
            }
            
            const statusClass = getStatusClass(lead.status);
            const interestClass = getInterestClass(lead.interesse);
            const leadNome = lead.nome || 'Nome não informado';
            const leadTelefone = lead.telefone || 'N/A';
            const leadStatus = lead.status_display || 'Indefinido';
            const leadInteresse = lead.interesse_display || 'N/A';
            
            html += `
                <tr>
                    <td>${leadNome}</td>
                    <td>${leadTelefone}</td>
                    <td><span class="badge ${statusClass}">${leadStatus}</span></td>
                    <td><span class="badge ${interestClass}">${leadInteresse}</span></td>
                    <td>${formatDate(lead.data_criacao)}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <a href="/leads/${lead.id}/" class="btn btn-outline-light" title="Ver detalhes">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="/vendedores/contato/${lead.id}/" class="btn btn-outline-primary" title="Registrar contato">
                                <i class="bi bi-telephone"></i>
                            </a>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        document.getElementById('contentBody').innerHTML = html;
        
        // Adicionar funcionalidade de busca
        const btnSearch = document.getElementById('btnSearchLeads');
        if (btnSearch) {
            btnSearch.addEventListener('click', function() {
                filterLeadsTable();
            });
        }
        
        const inputSearch = document.getElementById('searchLeads');
        if (inputSearch) {
            inputSearch.addEventListener('keyup', function(event) {
                if (event.key === 'Enter') {
                    filterLeadsTable();
                }
            });
        }
    } catch (error) {
        console.error('Erro ao renderizar tabela de leads:', error);
        document.getElementById('contentBody').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Erro ao renderizar leads:</strong> ${error.message || 'Ocorreu um erro inesperado ao mostrar os dados.'}
            </div>
            <div class="mt-3">
                <button class="btn btn-primary" onclick="fetchAndDisplayLeads()">
                    <i class="bi bi-arrow-clockwise"></i> Tentar novamente
                </button>
                <a href="/leads/lista/" class="btn btn-secondary ms-2">
                    <i class="bi bi-box-arrow-up-right"></i> Abrir em nova página
                </a>
            </div>
        `;
    }
}

// Função para filtrar a tabela de leads
function filterLeadsTable() {
    const input = document.getElementById('searchLeads');
    const filter = input.value.toUpperCase();
    const table = document.querySelector('.table');
    
    if (!table) {
        console.error('Tabela de leads não encontrada');
        return;
    }
    
    const tbody = table.querySelector('tbody');
    if (!tbody) {
        console.error('Corpo da tabela não encontrado');
        return;
    }
    
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const tdName = row.cells[0] ? (row.cells[0].textContent || '') : '';
        const tdPhone = row.cells[1] ? (row.cells[1].textContent || '') : '';
        
        if (tdName.toUpperCase().indexOf(filter) > -1 || tdPhone.toUpperCase().indexOf(filter) > -1) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Funções de formatação e utilidades
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return 'Data inválida';
        }
        return date.toLocaleDateString('pt-BR');
    } catch (e) {
        console.error('Erro ao formatar data:', e);
        return 'Data inválida';
    }
}

function getStatusClass(status) {
    if (!status) return 'bg-secondary';
    
    const statusClasses = {
        'novo': 'bg-info',
        'contatado': 'bg-primary',
        'qualificado': 'bg-warning',
        'negociacao': 'bg-info',
        'fechado': 'bg-success',
        'perdido': 'bg-danger'
    };
    
    return statusClasses[status.toLowerCase()] || 'bg-secondary';
}

function getInterestClass(interesse) {
    if (!interesse) return 'bg-secondary';
    
    const interestClasses = {
        'alto': 'bg-success',
        'medio': 'bg-warning',
        'baixo': 'bg-danger'
    };
    
    return interestClasses[interesse.toLowerCase()] || 'bg-secondary';
}

// Exportar funções para uso global
window.fetchAndDisplayLeads = fetchAndDisplayLeads;
