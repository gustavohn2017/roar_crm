/**
 * WhatsApp Button Integration - Script para sincronização automática do número de telefone com WhatsApp
 * Versão: 2.0.0 (23/05/2025)
 * 
 * Este script transforma o checkbox em um botão estilizado para melhor UX e permite
 * que o usuário sincronize o número de telefone com WhatsApp facilmente.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('[WhatsApp Integration] Script iniciado');
    
    // Encontrar elementos no DOM
    const checkbox = document.getElementById('id_is_whatsapp');
    const telefoneInput = document.getElementById('id_telefone');
    const whatsappInput = document.getElementById('id_whatsapp');
    
    if (!checkbox || !telefoneInput) {
        console.error('[WhatsApp Integration] Elementos não encontrados no DOM');
        return;
    }
    
    // Criar campo oculto para WhatsApp se não existir
    let whatsapp = whatsappInput;
    if (!whatsapp) {
        console.log('[WhatsApp Integration] Criando campo oculto para WhatsApp');
        whatsapp = document.createElement('input');
        whatsapp.type = 'hidden';
        whatsapp.id = 'id_whatsapp';
        whatsapp.name = 'whatsapp';
        telefoneInput.parentNode.appendChild(whatsapp);
    }
    
    // Converter o checkbox em um botão visualmente atraente
    const createWhatsAppButton = () => {
        // Esconder o checkbox original
        checkbox.style.display = 'none';
        
        // Criar o botão WhatsApp
        const whatsappButton = document.createElement('button');
        whatsappButton.type = 'button';
        whatsappButton.id = 'whatsapp-button';
        whatsappButton.className = checkbox.checked ? 
            'btn btn-sm btn-success d-flex align-items-center' : 
            'btn btn-sm btn-outline-success d-flex align-items-center';
        
        // Adicionar ícone e texto
        whatsappButton.innerHTML = `
            <i class="bi bi-whatsapp me-1"></i>
            <span id="whatsapp-btn-text">${checkbox.checked ? 'WhatsApp ativado' : 'Usar como WhatsApp'}</span>
            <div class="ms-2 d-flex align-items-center">
                <div id="whatsapp-indicator" class="rounded-circle ${checkbox.checked ? 'bg-light' : 'd-none'}" 
                     style="width: 8px; height: 8px;"></div>
            </div>
        `;
        
        // Substituir o label do checkbox pelo botão
        const checkboxLabel = checkbox.nextElementSibling;
        if (checkboxLabel) {
            checkboxLabel.parentNode.insertBefore(whatsappButton, checkboxLabel);
            checkboxLabel.style.display = 'none';
        } else {
            checkbox.parentNode.insertBefore(whatsappButton, checkbox.nextSibling);
        }
        
        // Adicionar evento de clique
        whatsappButton.addEventListener('click', function() {
            checkbox.checked = !checkbox.checked;
            
            // Atualizar estilo do botão
            this.className = checkbox.checked ? 
                'btn btn-sm btn-success d-flex align-items-center' : 
                'btn btn-sm btn-outline-success d-flex align-items-center';
            
            // Atualizar texto e indicador
            document.getElementById('whatsapp-btn-text').textContent = 
                checkbox.checked ? 'WhatsApp ativado' : 'Usar como WhatsApp';
            
            const indicator = document.getElementById('whatsapp-indicator');
            if (indicator) {
                if (checkbox.checked) {
                    indicator.classList.remove('d-none');
                } else {
                    indicator.classList.add('d-none');
                }
            }
            
            // Disparar evento de mudança para sincronizar o número
            const event = new Event('change');
            checkbox.dispatchEvent(event);
        });
    };
    
    // Função para sincronizar o telefone com WhatsApp
    function syncWhatsApp() {
        if (checkbox.checked) {
            whatsapp.value = telefoneInput.value;
            console.log('[WhatsApp Integration] Número sincronizado:', whatsapp.value);
            
            // Feedback visual para o usuário
            const existingMsg = document.getElementById('whatsapp-copy-msg');
            if (!existingMsg) {
                const msg = document.createElement('div');
                msg.id = 'whatsapp-copy-msg';
                msg.className = 'text-success small mt-2 ms-2 fade-in';
                msg.innerHTML = '<i class="bi bi-check-circle-fill"></i> Número copiado para WhatsApp';
                
                // Inserir após o botão
                const whatsappBtn = document.getElementById('whatsapp-button');
                if (whatsappBtn) {
                    whatsappBtn.parentNode.insertBefore(msg, whatsappBtn.nextSibling);
                } else {
                    checkbox.parentNode.appendChild(msg);
                }
                
                // Adicionar animação de fade-in
                msg.style.opacity = '0';
                msg.style.transition = 'opacity 0.3s ease-in-out';
                
                setTimeout(() => {
                    msg.style.opacity = '1';
                }, 10);
                
                // Remover a mensagem após 3 segundos
                setTimeout(() => {
                    msg.style.opacity = '0';
                    setTimeout(() => {
                        if (msg.parentNode) {
                            msg.parentNode.removeChild(msg);
                        }
                    }, 300);
                }, 3000);
            }
        } else {
            whatsapp.value = '';
            console.log('[WhatsApp Integration] Campo WhatsApp limpo');
        }
    }
    
    // Criar botão estilizado
    createWhatsAppButton();
    
    // Evento quando o checkbox é alterado
    checkbox.addEventListener('change', function() {
        console.log('[WhatsApp Integration] Estado alterado:', this.checked);
        syncWhatsApp();
    });
    
    // Evento quando o telefone é alterado
    telefoneInput.addEventListener('input', function() {
        if (checkbox.checked) {
            whatsapp.value = this.value;
            console.log('[WhatsApp Integration] WhatsApp atualizado:', whatsapp.value);
        }
    });
    
    // Verificar estado inicial
    if (checkbox.checked) {
        syncWhatsApp();
    }
    
    console.log('[WhatsApp Integration] Configuração concluída');
});