from django.db import models
from django.utils import timezone

class Lead(models.Model):
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('contatado', 'Contatado'),
        ('qualificado', 'Qualificado'),
        ('proposta', 'Proposta Enviada'),
        ('negociacao', 'Em Negociação'),
        ('fechado', 'Fechado'),
        ('perdido', 'Perdido'),
    ]
    
    INTEREST_CHOICES = [
        ('consorcio', 'Consórcio'),
        ('carta_credito', 'Carta de Crédito'),
        ('capital_giro', 'Capital de Giro'),
        ('financiamento', 'Financiamento'),
        ('emprestimo', 'Empréstimo'),
        ('outro', 'Outro'),
    ]
    
    SOURCE_CHOICES = [
        ('site', 'Website'),
        ('indicacao', 'Indicação'),
        ('redes_sociais', 'Redes Sociais'),
        ('ligacao', 'Ligação Direta'),
        ('email', 'Email Marketing'),
        ('evento', 'Evento'),
        ('parceiro', 'Parceiro'),
        ('importacao', 'Importação de Arquivo'),
        ('outro', 'Outro'),
    ]
    
    # Informações básicas
    nome = models.CharField(max_length=100)
    cpf_cnpj = models.CharField("CPF/CNPJ", max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    
    # Informações da empresa (caso seja pessoa jurídica)
    empresa = models.CharField("Empresa", max_length=100, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    faturamento_mensal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Informações de endereço
    cep = models.CharField("CEP", max_length=10, blank=True, null=True)
    logradouro = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField("Número", max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    
    # Informações de negócio
    interesse = models.CharField(max_length=20, choices=INTEREST_CHOICES, default='consorcio')
    valor_interesse = models.DecimalField("Valor de interesse", max_digits=12, decimal_places=2, blank=True, null=True)
    prazo_desejado = models.IntegerField("Prazo desejado (meses)", blank=True, null=True)
    
    # Gestão do lead
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='novo')
    fonte = models.CharField("Fonte", max_length=20, choices=SOURCE_CHOICES, default='site')
    responsavel = models.ForeignKey('auth.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='leads')
    prioridade = models.IntegerField(default=2, choices=[(1, 'Baixa'), (2, 'Média'), (3, 'Alta')])
    observacoes = models.TextField("Observações", blank=True, null=True)
    
    # Datas importantes
    data_criacao = models.DateTimeField("Data de criação", default=timezone.now)
    data_modificacao = models.DateTimeField("Última modificação", auto_now=True)
    data_ultimo_contato = models.DateTimeField("Data do último contato", blank=True, null=True)
    data_proxima_acao = models.DateTimeField("Data da próxima ação", blank=True, null=True)
    
    # Informações de importação
    arquivo_origem = models.CharField("Arquivo de origem", max_length=255, blank=True, null=True)
    importado_em = models.DateTimeField("Importado em", blank=True, null=True)
    
    def __str__(self):
        if self.empresa:
            return f"{self.nome} - {self.empresa}"
        return self.nome
    
    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ['-data_criacao']

