/**
 * Arquivo JavaScript principal para o Roar CRM
 * Contém funcionalidades comuns usadas em toda a aplicação
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicialização de tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicialização de popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Função para atualizar a data e hora atual
    function updateDateTime() {
        const datetimeElements = document.querySelectorAll('.current-datetime');
        if (datetimeElements.length > 0) {
            const now = new Date();
            const options = { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            const formattedDate = now.toLocaleDateString('pt-BR', options);
            
            datetimeElements.forEach(element => {
                element.textContent = formattedDate;
            });
        }
    }
    
    // Atualiza a hora a cada minuto
    updateDateTime();
    setInterval(updateDateTime, 60000);
    
    // Inicializa os elementos de data e hora do sistema
    const datetimeElement = document.getElementById('datetime');
    if (datetimeElement) {
        updateDateTime();
        setInterval(updateDateTime, 1000);
    }
});

// Função para mostrar notificações na aplicação
function showNotification(message, type = 'info') {
    const notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        // Cria o container de notificações se não existir
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Cria a notificação
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Adiciona a notificação ao container
    document.getElementById('notification-container').appendChild(notification);
    
    // Remove a notificação após 5 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 150);
    }, 5000);
}
