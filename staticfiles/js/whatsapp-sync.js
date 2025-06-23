/**
 * WhatsApp Sync - Script para sincronizar telefone com campo WhatsApp
 * Versão: 1.0.0 - 22/05/2025
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('WhatsApp Sync script carregado!');
    
    // Obter os elementos do formulário
    const whatsappCheckbox = document.getElementById('id_is_whatsapp');
    const telefoneInput = document.getElementById('id_telefone');
    const whatsappInput = document.getElementById('id_whatsapp');
    
    if (!whatsappCheckbox || !telefoneInput || !whatsappInput) {
        console.error('Elementos do formulário não encontrados', {
            checkbox: whatsappCheckbox,
            telefone: telefoneInput,
            whatsapp: whatsappInput
        });
        return;
    }
    
    console.log('Elementos encontrados, configurando eventos');
    
    // Evento de mudança no checkbox
    whatsappCheckbox.addEventListener('change', function() {
        console.log('Checkbox alterado:', this.checked);
        
        if (this.checked) {
            // Copiar o número para o WhatsApp
            whatsappInput.value = telefoneInput.value;
            console.log('Número copiado para WhatsApp:', whatsappInput.value);
            
            // Efeito visual
            const parentElement = whatsappCheckbox.closest('.form-check');
            parentElement.classList.add('text-success');
            
            // Notificação
            alert('Número copiado para WhatsApp: ' + telefoneInput.value);
        } else {
            // Limpar o campo
            whatsappInput.value = '';
            console.log('Campo WhatsApp limpo');
            
            // Remover efeito visual
            const parentElement = whatsappCheckbox.closest('.form-check');
            parentElement.classList.remove('text-success');
        }
    });
    
    // Evento de digitação no campo de telefone
    telefoneInput.addEventListener('input', function() {
        if (whatsappCheckbox.checked) {
            whatsappInput.value = this.value;
            console.log('WhatsApp atualizado conforme digitação:', this.value);
        }
    });
    
    console.log('WhatsApp Sync configurado com sucesso!');
});
