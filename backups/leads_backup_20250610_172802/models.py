from django.db import models
from django.utils import timezone

# Modelos de comunicação
class TemplateWhatsApp(models.Model):
    """Modelo para armazenar templates de mensagens WhatsApp."""
    nome = models.CharField("Nome do template", max_length=100)
    conteudo = models.TextField("Conteúdo da mensagem")
    pode_personalizar = models.BooleanField("Permite personalização", default=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Template de WhatsApp"
        verbose_name_plural = "Templates de WhatsApp"


class TemplateEmail(models.Model):
    """Modelo para armazenar templates de e-mail."""
    nome = models.CharField("Nome do template", max_length=100)
    assunto = models.CharField("Assunto do e-mail", max_length=200)
    conteudo = models.TextField("Conteúdo do e-mail")
    pode_personalizar = models.BooleanField("Permite personalização", default=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Template de E-mail"
        verbose_name_plural = "Templates de E-mail"


class HistoricoContato(models.Model):
    """Registro de contatos realizados com os leads via WhatsApp ou E-mail."""
    TIPO_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'E-mail'),
        ('ligacao', 'Ligação'),
        ('reuniao', 'Reunião'),
        ('outro', 'Outro')
    ]
    
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='historico_comunicacao')
    tipo = models.CharField("Tipo de contato", max_length=20, choices=TIPO_CHOICES)
    conteudo = models.TextField("Conteúdo enviado")
    resposta = models.TextField("Resposta recebida", blank=True, null=True)
    data_envio = models.DateTimeField(default=timezone.now)
    data_resposta = models.DateTimeField(blank=True, null=True)
    resultado = models.CharField("Resultado", max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} para {self.lead.nome} em {self.data_envio.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Histórico de Contato"
        verbose_name_plural = "Históricos de Contato"


# Modelo principal de Lead
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

