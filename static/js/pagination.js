
/**
 * Script para paginação de leads e outras listagens.
 */

const pagination = {
    currentPage: 1,
    pageSize: 10,
    totalItems: 0,
    totalPages: 1,

    init: function(endpoint, renderFunction) {
        this.endpoint = endpoint;
        this.renderFunction = renderFunction;
        this.fetchAndDisplay();
    },

    fetchAndDisplay: function(page = 1) {
        this.currentPage = page;
        
        // Idealmente, o indicador de loading seria uma função global
        if (typeof showLoading === 'function') {
            showLoading('Carregando...');
        }

        const url = `${this.endpoint}?page=${this.currentPage}&page_size=${this.pageSize}`;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.totalItems = data.pagination.total_items;
                this.totalPages = data.pagination.total_pages;
                this.renderFunction(data.results); // Assumindo que os itens estão em 'results'
                this.renderPaginationControls();
            })
            .catch(error => {
                console.error("Erro ao buscar dados paginados:", error);
                const contentBody = document.getElementById('contentBody');
                if(contentBody) {
                    contentBody.innerHTML = `<div class="alert alert-danger">Erro ao carregar dados. Tente novamente.</div>`;
                }
            });
    },

    renderPaginationControls: function() {
        const paginationContainer = document.getElementById('pagination-controls');
        if (!paginationContainer) {
            console.warn("Elemento com id 'pagination-controls' não encontrado para renderizar a paginação.");
            return;
        }

        if (this.totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        let html = '<nav aria-label="Page navigation"><ul class="pagination justify-content-center">';

        // Botão Anterior
        html += `<li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="pagination.fetchAndDisplay(${this.currentPage - 1})">Anterior</a>
                 </li>`;

        // Lógica para exibir os números das páginas (simplificada)
        for (let i = 1; i <= this.totalPages; i++) {
            if (i === this.currentPage) {
                html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
            } else {
                html += `<li class="page-item"><a class="page-link" href="#" onclick="pagination.fetchAndDisplay(${i})">${i}</a></li>`;
            }
        }

        // Botão Próximo
        html += `<li class="page-item ${this.currentPage === this.totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="pagination.fetchAndDisplay(${this.currentPage + 1})">Próximo</a>
                 </li>`;

        html += '</ul></nav>';
        paginationContainer.innerHTML = html;
    }
};
