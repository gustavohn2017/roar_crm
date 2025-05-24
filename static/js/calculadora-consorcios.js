/**
 * Calculadora de Consórcios - Lions CRM
 * Script para a nova interface de calculadoras de consórcio
 * Versão 2.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // ===== CONFIGURAÇÕES COMUNS =====
    const formatter = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2
    });

    // Animação de resultado
    function animateResult(elementId) {
        const element = document.getElementById(elementId);
        element.classList.add('animar-resultado');
        
        setTimeout(() => {
            element.classList.remove('animar-resultado');
        }, 700);
    }
    
    // Função para adicionar efeito de carregamento
    function addLoadingEffect(button, callback) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="bi bi-hourglass-split"></i> Calculando...';
        button.disabled = true;
        
        setTimeout(() => {
            callback();
            button.innerHTML = originalText;
            button.disabled = false;
        }, 600);
    }

    // ===== CALCULADORA DE CONSÓRCIO AUTO =====
    
    // Atualizar valores dos sliders
    const carRate = document.getElementById('carRate');
    const carRateValue = document.getElementById('carRateValue');
    
    carRate.addEventListener('input', function() {
        carRateValue.textContent = this.value + '%';
    });
    
    const carEntryFee = document.getElementById('carEntryFee');
    const carEntryFeeValue = document.getElementById('carEntryFeeValue');
    
    carEntryFee.addEventListener('input', function() {
        carEntryFeeValue.textContent = this.value + '%';
    });
    
    const carFundFee = document.getElementById('carFundFee');
    const carFundFeeValue = document.getElementById('carFundFeeValue');
    
    carFundFee.addEventListener('input', function() {
        carFundFeeValue.textContent = this.value + '%';
    });
    
    // Botão para calcular
    document.getElementById('calculateCarBtn').addEventListener('click', function() {
        addLoadingEffect(this, calculateCarConsortium);
    });

    // Calcular automaticamente ao alterar valores
    ['carValue', 'carPlanDuration', 'carRate', 'carEntryFee', 'carFundFee'].forEach(id => {
        document.getElementById(id).addEventListener('change', function() {
            calculateCarConsortium(false);
        });
    });
    
    // Preparar dados para o PDF
    document.getElementById('carProposalForm').addEventListener('submit', function() {
        const button = document.getElementById('carGenerateProposalBtn');
        button.innerHTML = '<i class="bi bi-hourglass-split"></i> Gerando PDF...';
        button.disabled = true;
        
        // Atualizar todos os campos ocultos
        updateCarProposalFormData();
    });
    
    // Atualização dos campos do formulário PDF
    function updateCarProposalFormData() {
        const carValue = parseFloat(document.getElementById('carValue').value);
        const planDuration = parseInt(document.getElementById('carPlanDuration').value);
        const adminRate = parseFloat(document.getElementById('carRate').value) / 100;
        const fundFee = parseFloat(document.getElementById('carFundFee').value) / 100;
        const entryFee = parseFloat(document.getElementById('carEntryFee').value) / 100;
        
        const adminFeeTotal = carValue * adminRate;
        const fundFeeTotal = carValue * fundFee;
        const entryFeeTotal = carValue * entryFee;
        const totalPlanValue = carValue + adminFeeTotal + fundFeeTotal + entryFeeTotal;
        const monthlyPayment = totalPlanValue / planDuration;
        
        document.getElementById('carProposalCreditValue').value = carValue.toFixed(2);
        document.getElementById('carProposalDuration').value = planDuration;
        document.getElementById('carProposalAdminRate').value = (adminRate * 100).toFixed(2);
        document.getElementById('carProposalMonthlyPayment').value = monthlyPayment.toFixed(2);
        document.getElementById('carProposalTotalValue').value = totalPlanValue.toFixed(2);
    }
    
    // Função para calcular consórcio de automóvel
    function calculateCarConsortium(animate = true) {
        // Obter valores do formulário
        const carValue = parseFloat(document.getElementById('carValue').value);
        const planDuration = parseInt(document.getElementById('carPlanDuration').value);
        const adminRate = parseFloat(document.getElementById('carRate').value) / 100;
        const fundFee = parseFloat(document.getElementById('carFundFee').value) / 100;
        const entryFee = parseFloat(document.getElementById('carEntryFee').value) / 100;
        
        // Calcular valores
        const adminFeeTotal = carValue * adminRate;
        const fundFeeTotal = carValue * fundFee;
        const entryFeeTotal = carValue * entryFee;
        const totalPlanValue = carValue + adminFeeTotal + fundFeeTotal + entryFeeTotal;
        const monthlyPayment = totalPlanValue / planDuration;
        
        // Atualizar resultados
        document.getElementById('carMonthlyPayment').textContent = formatter.format(monthlyPayment);
        document.getElementById('carTotalCredit').textContent = formatter.format(carValue);
        document.getElementById('carTotalAdminFee').textContent = `${formatter.format(adminFeeTotal)} (${(adminRate * 100).toFixed(1)}%)`;
        document.getElementById('carTotalFundFee').textContent = `${formatter.format(fundFeeTotal)} (${(fundFee * 100).toFixed(1)}%)`;
        document.getElementById('carTotalEntryFee').textContent = `${formatter.format(entryFeeTotal)} (${(entryFee * 100).toFixed(1)}%)`;
        document.getElementById('carTotalPlanValue').textContent = formatter.format(totalPlanValue);
        
        // Formatar prazo
        const years = Math.floor(planDuration / 12);
        const remainingMonths = planDuration % 12;
        document.getElementById('carPlanDurationResult').textContent = 
            `${planDuration} meses (${years} anos${remainingMonths ? ' e ' + remainingMonths + ' meses' : ''})`;
        
        // Animar resultado se solicitado
        if (animate) {
            animateResult('carResultPrincipal');
        }
        
        // Atualizar campos ocultos do formulário para geração de PDF
        updateCarProposalFormData();
    }

    // ===== CALCULADORA DE CONSÓRCIO IMOBILIÁRIO =====
    
    // Atualizar valores dos sliders
    const propertyRate = document.getElementById('propertyRate');
    const propertyRateValue = document.getElementById('propertyRateValue');
    
    propertyRate.addEventListener('input', function() {
        propertyRateValue.textContent = this.value + '%';
    });
    
    const propertyEntryFee = document.getElementById('propertyEntryFee');
    const propertyEntryFeeValue = document.getElementById('propertyEntryFeeValue');
    
    propertyEntryFee.addEventListener('input', function() {
        propertyEntryFeeValue.textContent = this.value + '%';
    });
    
    const propertyFundFee = document.getElementById('propertyFundFee');
    const propertyFundFeeValue = document.getElementById('propertyFundFeeValue');
    
    propertyFundFee.addEventListener('input', function() {
        propertyFundFeeValue.textContent = this.value + '%';
    });
    
    // Botão para calcular
    document.getElementById('calculatePropertyBtn').addEventListener('click', function() {
        addLoadingEffect(this, calculatePropertyConsortium);
    });
    
    // Calcular automaticamente ao alterar valores
    ['propertyValue', 'propertyPlanDuration', 'propertyRate', 'propertyEntryFee', 'propertyFundFee'].forEach(id => {
        document.getElementById(id).addEventListener('change', function() {
            calculatePropertyConsortium(false);
        });
    });
    
    // Preparar dados para o PDF
    document.getElementById('propertyProposalForm').addEventListener('submit', function() {
        const button = document.getElementById('propertyGenerateProposalBtn');
        button.innerHTML = '<i class="bi bi-hourglass-split"></i> Gerando PDF...';
        button.disabled = true;
        
        // Atualizar todos os campos ocultos
        updatePropertyProposalFormData();
    });
    
    // Atualização dos campos do formulário PDF
    function updatePropertyProposalFormData() {
        const propertyValue = parseFloat(document.getElementById('propertyValue').value);
        const planDuration = parseInt(document.getElementById('propertyPlanDuration').value);
        const adminRate = parseFloat(document.getElementById('propertyRate').value) / 100;
        const fundFee = parseFloat(document.getElementById('propertyFundFee').value) / 100;
        const entryFee = parseFloat(document.getElementById('propertyEntryFee').value) / 100;
        
        const adminFeeTotal = propertyValue * adminRate;
        const fundFeeTotal = propertyValue * fundFee;
        const entryFeeTotal = propertyValue * entryFee;
        const totalPlanValue = propertyValue + adminFeeTotal + fundFeeTotal + entryFeeTotal;
        const monthlyPayment = totalPlanValue / planDuration;
        
        document.getElementById('propertyProposalCreditValue').value = propertyValue.toFixed(2);
        document.getElementById('propertyProposalDuration').value = planDuration;
        document.getElementById('propertyProposalAdminRate').value = (adminRate * 100).toFixed(2);
        document.getElementById('propertyProposalMonthlyPayment').value = monthlyPayment.toFixed(2);
        document.getElementById('propertyProposalTotalValue').value = totalPlanValue.toFixed(2);
    }
    
    // Função para calcular consórcio imobiliário
    function calculatePropertyConsortium(animate = true) {
        // Obter valores do formulário
        const propertyValue = parseFloat(document.getElementById('propertyValue').value);
        const planDuration = parseInt(document.getElementById('propertyPlanDuration').value);
        const adminRate = parseFloat(document.getElementById('propertyRate').value) / 100;
        const fundFee = parseFloat(document.getElementById('propertyFundFee').value) / 100;
        const entryFee = parseFloat(document.getElementById('propertyEntryFee').value) / 100;
        
        // Calcular valores
        const adminFeeTotal = propertyValue * adminRate;
        const fundFeeTotal = propertyValue * fundFee;
        const entryFeeTotal = propertyValue * entryFee;
        const totalPlanValue = propertyValue + adminFeeTotal + fundFeeTotal + entryFeeTotal;
        const monthlyPayment = totalPlanValue / planDuration;
        
        // Atualizar resultados
        document.getElementById('propertyMonthlyPayment').textContent = formatter.format(monthlyPayment);
        document.getElementById('propertyTotalCredit').textContent = formatter.format(propertyValue);
        document.getElementById('propertyTotalAdminFee').textContent = `${formatter.format(adminFeeTotal)} (${(adminRate * 100).toFixed(1)}%)`;
        document.getElementById('propertyTotalFundFee').textContent = `${formatter.format(fundFeeTotal)} (${(fundFee * 100).toFixed(1)}%)`;
        document.getElementById('propertyTotalEntryFee').textContent = `${formatter.format(entryFeeTotal)} (${(entryFee * 100).toFixed(1)}%)`;
        document.getElementById('propertyTotalPlanValue').textContent = formatter.format(totalPlanValue);
        
        // Formatar prazo
        const years = Math.floor(planDuration / 12);
        const remainingMonths = planDuration % 12;
        document.getElementById('propertyPlanDurationResult').textContent = 
            `${planDuration} meses (${years} anos${remainingMonths ? ' e ' + remainingMonths + ' meses' : ''})`;
        
        // Animar resultado se solicitado
        if (animate) {
            animateResult('propertyResultPrincipal');
        }
        
        // Atualizar campos ocultos do formulário para geração de PDF
        updatePropertyProposalFormData();
    }
    
    // ===== FUNÇÕES DE ACESSIBILIDADE E UX =====
    
    // Atalho de teclado para calcular (Ctrl+Enter)
    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.key === 'Enter') {
            const activeTab = document.querySelector('.tab-pane.active');
            if (activeTab) {
                const calculateBtn = activeTab.querySelector('button[id^="calculate"]');
                if (calculateBtn) {
                    calculateBtn.click();
                }
            }
        }
    });
    
    // Salvar estado no localStorage
    function saveCalculatorState() {
        const state = {
            // Auto
            carValue: document.getElementById('carValue').value,
            carPlanDuration: document.getElementById('carPlanDuration').value,
            carRate: document.getElementById('carRate').value,
            carEntryFee: document.getElementById('carEntryFee').value,
            carFundFee: document.getElementById('carFundFee').value,
            
            // Imóvel
            propertyValue: document.getElementById('propertyValue').value,
            propertyPlanDuration: document.getElementById('propertyPlanDuration').value,
            propertyRate: document.getElementById('propertyRate').value,
            propertyEntryFee: document.getElementById('propertyEntryFee').value,
            propertyFundFee: document.getElementById('propertyFundFee').value,
            
            // Aba ativa
            activeTabId: document.querySelector('.tab-pane.show.active').id
        };
        
        localStorage.setItem('lionsCalculadoraConsorcio', JSON.stringify(state));
    }
    
    // Restaurar estado do localStorage
    function restoreCalculatorState() {
        const savedState = localStorage.getItem('lionsCalculadoraConsorcio');
        if (savedState) {
            const state = JSON.parse(savedState);
            
            // Restaurar valores
            Object.entries(state).forEach(([key, value]) => {
                if (key !== 'activeTabId') {
                    const element = document.getElementById(key);
                    if (element) {
                        element.value = value;
                        // Trigger input event para atualizar displays dos sliders
                        element.dispatchEvent(new Event('input'));
                    }
                }
            });
            
            // Restaurar aba ativa
            if (state.activeTabId) {
                const tabToActivate = document.querySelector(`[data-bs-target="#${state.activeTabId}"]`);
                if (tabToActivate) {
                    const tab = new bootstrap.Tab(tabToActivate);
                    tab.show();
                }
            }
            
            // Recalcular valores
            calculateCarConsortium(false);
            calculatePropertyConsortium(false);
        }
    }
    
    // Auto-save ao alterar valores
    document.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('change', saveCalculatorState);
    });
    
    // Monitorar mudança de abas para salvar estado
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', saveCalculatorState);
    });
    
    // Inicializar calculadoras
    calculateCarConsortium(false);
    calculatePropertyConsortium(false);
    
    // Restaurar estado anterior
    restoreCalculatorState();
});
