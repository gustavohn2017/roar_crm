/**
 * Quick Lead Registration Form Javascript
 * Este script melhora a experiência do formulário modal de cadastro rápido
 * com validação, formatação automática e melhorias de UX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configura foco automático no primeiro campo quando o formulário é aberto
    const setupAutoFocus = () => {
        const forms = document.querySelectorAll('form.needs-validation');
        forms.forEach(form => {
            // Encontra o primeiro input visível
            const firstInput = form.querySelector('input:not([type="hidden"]):not([disabled])');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        });
        
        // Configurar navegação com Tab otimizada
        const addTabBehavior = () => {
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && this.tagName !== 'TEXTAREA') {
                        e.preventDefault();
                        const form = this.closest('form');
                        
                        // Se for o último campo, submeter o formulário
                        const formInputs = Array.from(form.querySelectorAll('input:not([type="hidden"]), select, textarea'));
                        const currentIndex = formInputs.indexOf(this);
                        
                        if (currentIndex < formInputs.length - 1) {
                            formInputs[currentIndex + 1].focus();
                        } else {
                            // Último campo, verificar se tem botão de confirmação
                            const confirmBtn = form.querySelector('.btn-confirm');
                            if (confirmBtn) {
                                confirmBtn.click();
                            } else {
                                form.submit();
                            }
                        }
                    }
                });
            });
        };
        
        addTabBehavior();
    };
    
    // Executa configuração de foco automático
    setupAutoFocus();

    // Formato para telefone e WhatsApp
    const applyPhoneMask = (input) => {
        let value = input.value.replace(/\D/g, '');
        if (value.length > 11) value = value.slice(0, 11);
        
        if (value.length > 10) {
            value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
        } else if (value.length > 2) {
            value = value.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
        }
        
        input.value = value;
    };

    // Formato para valores monetários
    const applyMoneyMask = (input) => {
        let value = input.value.replace(/\D/g, '');
        if (value.length > 0) {
            value = (parseInt(value) / 100).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        input.value = value;
    };
    
    // Adicionar máscara aos campos de telefone
    document.querySelectorAll('.phone-mask').forEach(function(input) {
        input.addEventListener('input', function() {
            applyPhoneMask(this);
        });
    });
    
    // Adicionar máscara aos campos monetários
    document.querySelectorAll('.money-mask').forEach(function(input) {
        input.addEventListener('input', function() {
            applyMoneyMask(this);
        });
    });
      // Validação de formulário com feedback visual e botões interativos
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        // Função para validar o formulário e atualizar estado do botão
        const validateForm = () => {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                }
            });
            
            // Atualizar o botão de confirmar
            const confirmBtn = form.querySelector('.btn-confirm');
            if (confirmBtn) {
                if (isValid) {
                    confirmBtn.classList.remove('disabled');
                } else {
                    confirmBtn.classList.add('disabled');
                }
            }
            
            return isValid;
        };
        
        // Validação em tempo real para cada campo
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('input', validateForm);
        });
        
        // Executar validação inicial
        validateForm();
        
        // Validação no envio do formulário
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Melhoria de UX: autocomplete para campos de endereço via CEP
    const cepField = document.getElementById('id_cep');
    if (cepField) {
        cepField.addEventListener('blur', async function() {
            const cep = this.value.replace(/\D/g, '');
            
            if (cep.length !== 8) return;
            
            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                const data = await response.json();
                
                if (!data.erro) {
                    document.getElementById('id_logradouro').value = data.logradouro;
                    document.getElementById('id_bairro').value = data.bairro;
                    document.getElementById('id_cidade').value = data.localidade;
                    document.getElementById('id_estado').value = data.uf;
                    
                    // Foco no número após preenchimento automático
                    document.getElementById('id_numero').focus();
                }
            } catch (error) {
                console.error('Erro ao buscar CEP:', error);
            }
        });
    }

    // Modal de confirmação ao salvar lead
    const quickLeadForm = document.getElementById('quickLeadForm');
    const submitBtn = document.getElementById('quickLeadSaveBtn');
    
    if (submitBtn && quickLeadForm) {
        submitBtn.addEventListener('click', function() {
            const nameField = quickLeadForm.querySelector('#id_nome');
            const phoneField = quickLeadForm.querySelector('#id_telefone');
            
            if (!nameField.value.trim()) {
                nameField.classList.add('is-invalid');
                return;
            }
            
            if (!phoneField.value.trim()) {
                phoneField.classList.add('is-invalid');
                return;
            }
            
            quickLeadForm.submit();
        });
    }
      // Reset do formulário ao fechar o modal
    const quickLeadModal = document.getElementById('quickLeadModal');
    if (quickLeadModal) {
        quickLeadModal.addEventListener('hidden.bs.modal', function () {
            const form = this.querySelector('form');
            
            if (form) {
                // Reset do formulário
                form.reset();
                form.classList.remove('was-validated');
                
                // Limpar as classes de validação
                form.querySelectorAll('.is-invalid').forEach(field => {
                    field.classList.remove('is-invalid');
                });
                
                // Resetar o campo WhatsApp e o checkbox
                const whatsappInput = form.querySelector('#id_whatsapp');
                const whatsappCheckbox = form.querySelector('#id_is_whatsapp');
                
                if (whatsappInput) {
                    whatsappInput.value = '';
                }
                
                if (whatsappCheckbox) {
                    whatsappCheckbox.checked = false;
                    whatsappCheckbox.closest('.form-check').classList.remove('text-success');
                }
                
                // Remover quaisquer mensagens de notificação
                form.querySelectorAll('.fade-message').forEach(el => el.remove());
            }
        });
        
        // Quando o modal é mostrado, focar no campo de nome
        quickLeadModal.addEventListener('shown.bs.modal', function () {
            const nameField = this.querySelector('#id_nome');
            if (nameField) {
                nameField.focus();
            }
        });
    }
      // Gerenciar checkbox WhatsApp - copia o número para campo whatsapp quando marcado
    const whatsappCheckbox = document.getElementById('id_is_whatsapp');
    const telefoneInput = document.getElementById('id_telefone');
    const whatsappInput = document.getElementById('id_whatsapp');
    
    if (whatsappCheckbox && telefoneInput && whatsappInput) {
        // Quando o checkbox é marcado/desmarcado
        whatsappCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // Copiar o número de telefone para o campo WhatsApp
                whatsappInput.value = telefoneInput.value;
                
                // Mostrar confirmação visual
                whatsappCheckbox.closest('.form-check').classList.add('text-success');
                
                // Mostrar mensagem de confirmação
                const notificationMsg = document.createElement('div');
                notificationMsg.className = 'mt-1 small text-success fade-message';
                notificationMsg.innerHTML = '<i class="bi bi-check-circle-fill"></i> Número copiado para WhatsApp';
                
                // Inserir mensagem após o checkbox
                const parentElement = whatsappCheckbox.closest('.form-check');
                parentElement.appendChild(notificationMsg);
                
                // Remover mensagem após 2 segundos
                setTimeout(() => {
                    notificationMsg.remove();
                }, 2000);
            } else {
                // Limpar o campo WhatsApp quando desmarcado
                whatsappInput.value = '';
                whatsappCheckbox.closest('.form-check').classList.remove('text-success');
            }
        });
        
        // Se o telefone mudar, atualizar o WhatsApp se o checkbox estiver marcado
        telefoneInput.addEventListener('input', function() {
            if (whatsappCheckbox.checked) {
                whatsappInput.value = this.value;
            }
        });
    }
});