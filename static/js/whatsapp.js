
/**
 * Script unificado para funcionalidades do WhatsApp.
 * Transforma o checkbox de "Usar como WhatsApp" em um botão interativo
 * e sincroniza o número de telefone com o campo WhatsApp.
 */

document.addEventListener('DOMContentLoaded', function() {
    const checkbox = document.getElementById('id_is_whatsapp');
    const telefoneInput = document.getElementById('id_telefone');
    let whatsappInput = document.getElementById('id_whatsapp');

    if (!checkbox || !telefoneInput) {
        // Não executa se os campos essenciais não estiverem na página
        return;
    }

    // Garante que o campo whatsapp exista, mesmo que oculto
    if (!whatsappInput) {
        whatsappInput = document.createElement('input');
        whatsappInput.type = 'hidden';
        whatsappInput.id = 'id_whatsapp';
        whatsappInput.name = 'whatsapp';
        telefoneInput.parentNode.insertBefore(whatsappInput, telefoneInput.nextSibling);
    }

    // --- Funções --- 

    const syncWhatsAppNumber = () => {
        if (checkbox.checked) {
            whatsappInput.value = telefoneInput.value;
        } else {
            whatsappInput.value = '';
        }
    };

    const updateButtonUI = (button) => {
        const isChecked = checkbox.checked;
        const textSpan = button.querySelector('span');
        const indicator = button.querySelector('#whatsapp-indicator');

        button.className = isChecked 
            ? 'btn btn-sm btn-success d-flex align-items-center' 
            : 'btn btn-sm btn-outline-success d-flex align-items-center';
        
        if(textSpan) textSpan.textContent = isChecked ? 'WhatsApp Ativado' : 'Usar como WhatsApp';
        if(indicator) indicator.classList.toggle('d-none', !isChecked);
    };

    const createWhatsAppButton = () => {
        checkbox.style.display = 'none'; // Esconde o checkbox original

        const button = document.createElement('button');
        button.type = 'button';
        button.id = 'whatsapp-toggle-button';
        button.innerHTML = `
            <i class="bi bi-whatsapp me-1"></i>
            <span></span>
            <div class="ms-2 d-flex align-items-center">
                <div id="whatsapp-indicator" class="rounded-circle bg-light" style="width: 8px; height: 8px;"></div>
            </div>
        `;

        // Insere o botão no lugar do label do checkbox
        const label = checkbox.closest('label') || checkbox.nextElementSibling;
        if (label && label.parentNode) {
            label.parentNode.insertBefore(button, label);
            if(label.tagName === 'LABEL') label.style.display = 'none';
        } else {
            checkbox.parentNode.insertBefore(button, checkbox.nextSibling);
        }

        updateButtonUI(button); // Define o estado inicial

        button.addEventListener('click', () => {
            checkbox.checked = !checkbox.checked;
            updateButtonUI(button);
            syncWhatsAppNumber();
        });
    };

    // --- Inicialização ---

    createWhatsAppButton();

    // Sincroniza quando o número de telefone muda
    telefoneInput.addEventListener('input', syncWhatsAppNumber);

    // Sincroniza no carregamento da página, caso o checkbox já venha marcado
    syncWhatsAppNumber();
});
