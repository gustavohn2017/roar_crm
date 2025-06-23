// Leads Pagination Script
let currentPage = 1;
const pageSize = 10;

// Function to fetch and display leads with pagination
function fetchAndDisplayLeads(page = 1) {
    // Set the current page
    currentPage = page;
    
    // Show loading indicator
    showLoading('Meus Leads');
    updateContentHeader('Meus Leads', 'Leads disponíveis para contato');
    
    // Fetch leads with pagination parameters
    fetch(`/main/api/leads/?page=${page}&page_size=${pageSize}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const contentBody = document.getElementById('contentBody');
            
            // Handle case with no leads
            if (!data || !data.leads || data.leads.length === 0) {
                contentBody.innerHTML = `
                    <div class="empty-state">
                        <i class="bi bi-people"></i>
                        <h3>Nenhum lead disponível</h3>
                        <p>Não há leads disponíveis para contato no momento.</p>
                        <div class="mt-4">
                            <button class="btn btn-primary me-2" onclick="openQuickLeadModal()">
                                <i class="bi bi-person-plus"></i> Cadastrar Novo Lead
                            </button>
                            <a href="/leads/" class="btn btn-secondary">
                                <i class="bi bi-list-ul"></i> Ver Todos os Leads
                            </a>
                        </div>
                    </div>
                `;
                return;
            }
            
            const leads = data.leads;
            const pagination = data.pagination;
            
            // Build leads table
            let html = `
                <div class="leads-container">
                    <div class="leads-actions">
                        <div class="filters">
                            <div class="input-group">
                                <span class="input-group-text"><i class="bi bi-search"></i></span>
                                <input type="text" class="form-control" id="leadSearch" placeholder="Buscar leads..." onkeyup="filterLeads()">
                            </div>
                            <div class="filter-dropdowns">
                                <select class="form-select" id="filterStatus" onchange="filterLeads()">
                                    <option value="">Status</option>
                                    <option value="novo">Novo</option>
                                    <option value="contatado">Contatado</option>
                                    <option value="qualificado">Qualificado</option>
                                    <option value="proposta">Proposta</option>
                                    <option value="negociacao">Negociação</option>
                                    <option value="fechado">Fechado</option>
                                    <option value="perdido">Perdido</option>
                                </select>
                                <select class="form-select" id="filterInteresse" onchange="filterLeads()">
                                    <option value="">Interesse</option>
                                    <option value="consorcio">Consórcio</option>
                                    <option value="carta_credito">Carta de Crédito</option>
                                    <option value="capital_giro">Capital de Giro</option>
                                    <option value="financiamento">Financiamento</option>
                                    <option value="emprestimo">Empréstimo</option>
                                    <option value="outro">Outro</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="table-responsive">
                        <table class="table table-hover leads-table">
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>Telefone</th>
                                    <th>Status</th>
                                    <th>Interesse</th>
                                    <th>Último Contato</th>
                                    <th>Ações</th>
                                </tr>
                            </thead>
                            <tbody id="leadsTableBody">`;
            
            // Add leads rows
            leads.forEach(lead => {
                const ultimoContato = lead.ultimo_contato ? new Date(lead.ultimo_contato).toLocaleDateString() : 'Nunca contatado';
                const statusClass = getStatusClass(lead.status);
                
                html += `
                    <tr data-status="${lead.status}" data-interesse="${lead.interesse}" data-search="${lead.nome.toLowerCase()} ${lead.email ? lead.email.toLowerCase() : ''}">
                        <td>
                            <div class="lead-name">
                                <strong>${lead.nome}</strong>
                                ${lead.email ? `<div class="lead-email">${lead.email}</div>` : ''}
                            </div>
                        </td>
                        <td>${lead.telefone || lead.whatsapp || '-'}</td>
                        <td><span class="status-badge ${statusClass}">${getStatusName(lead.status)}</span></td>
                        <td>${getInteresseName(lead.interesse) || '-'}</td>
                        <td>${ultimoContato}</td>
                        <td>
                            <div class="action-buttons">
                                <a href="/main/contato/${lead.id}/" class="btn btn-sm btn-outline-primary" title="Registrar Contato">
                                    <i class="bi bi-telephone"></i>
                                </a>
                                <a href="/main/lead/${lead.id}/" class="btn btn-sm btn-outline-secondary" title="Ver Detalhes">
                                    <i class="bi bi-eye"></i>
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
                    
                    <!-- Pagination -->
                    <nav aria-label="Navegação de páginas" class="mt-4">
                        <ul class="pagination justify-content-center">
                            <li class="page-item ${!pagination.has_previous ? 'disabled' : ''}">
                                <a class="page-link" href="#" onclick="fetchAndDisplayLeads(${currentPage - 1}); return false;" aria-label="Anterior">
                                    <span aria-hidden="true">&laquo;</span>
                                </a>
                            </li>
            `;
            
            // Create numbered pages
            for (let i = 1; i <= pagination.total_pages; i++) {
                html += `
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="fetchAndDisplayLeads(${i}); return false;">${i}</a>
                    </li>
                `;
            }
            
            html += `
                            <li class="page-item ${!pagination.has_next ? 'disabled' : ''}">
                                <a class="page-link" href="#" onclick="fetchAndDisplayLeads(${currentPage + 1}); return false;" aria-label="Próximo">
                                    <span aria-hidden="true">&raquo;</span>
                                </a>
                            </li>
                        </ul>
                    </nav>
                    
                    <div class="text-center text-muted mt-2">
                        <small>Mostrando ${leads.length} de ${pagination.total_items} leads - Página ${pagination.current_page} de ${pagination.total_pages}</small>
                    </div>
                </div>
            `;
            
            contentBody.innerHTML = html;
            
            // Update the page title
            currentTool = 'leads';
        })
        .catch(error => {
            console.error('Erro ao buscar leads:', error);
            
            // Fallback for error handling
            const contentBody = document.getElementById('contentBody');
            contentBody.innerHTML = `
                <div class="error-state">
                    <i class="bi bi-exclamation-triangle"></i>
                    <h3>Erro ao carregar leads</h3>
                    <p>Não foi possível carregar a lista de leads. Tente novamente mais tarde.</p>
                    <div class="mt-3">
                        <button class="btn btn-primary" onclick="fetchAndDisplayLeads()">
                            <i class="bi bi-arrow-repeat"></i> Tentar Novamente
                        </button>
                    </div>
                </div>
            `;
        });
}

// Helper function to add the pagination styles
function addPaginationStyles() {
    // Check if pagination styles already exist
    if (!document.getElementById('pagination-styles')) {
        const style = document.createElement('style');
        style.id = 'pagination-styles';
        style.textContent = `
            /* Pagination styles */
            .pagination {
                display: flex;
                padding-left: 0;
                list-style: none;
                border-radius: 0.25rem;
            }
            
            .page-link {
                position: relative;
                display: block;
                padding: 0.5rem 0.75rem;
                margin-left: -1px;
                line-height: 1.25;
                color: var(--color-gold);
                background-color: var(--color-dark-lighter);
                border: 1px solid var(--color-dark-light);
                text-decoration: none;
            }
            
            .page-link:hover {
                z-index: 2;
                color: var(--color-dark);
                background-color: var(--color-gold);
                border-color: var(--color-gold);
            }
            
            .page-item.active .page-link {
                z-index: 3;
                color: var(--color-dark);
                background-color: var(--color-gold);
                border-color: var(--color-gold);
            }
            
            .page-item.disabled .page-link {
                color: var(--color-text-muted);
                pointer-events: none;
                cursor: auto;
                background-color: var(--color-dark-medium);
                border-color: var(--color-dark-light);
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize pagination styles when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    addPaginationStyles();
});
