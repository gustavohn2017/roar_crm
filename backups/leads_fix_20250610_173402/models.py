"""
Modelos consolidados para gestão de leads.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Lead(models.Model):
    """Modelo principal para gerenciamento de leads."""
    
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
    
    PRIORITY_CHOICES = [
        (1, 'Baixa'),
        (2, 'Média'),
        (3, 'Alta'),
    ]
    
    # Informações básicas
    nome = models.CharField('Nome', max_length=100)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=20, blank=True, null=True)
    email = models.EmailField('E-mail', blank=True, null=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True, null=True)
    
    # Informações empresariais
    empresa = models.CharField('Empresa', max_length=100, blank=True, null=True)
    cargo = models.CharField('Cargo', max_length=100, blank=True, null=True)
    faturamento_mensal = models.DecimalField('Faturamento Mensal', max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Endereço
    cep = models.CharField('CEP', max_length=10, blank=True, null=True)
    logradouro = models.CharField('Logradouro', max_length=100, blank=True, null=True)
    numero = models.CharField('Número', max_length=10, blank=True, null=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True, null=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True, null=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True, null=True)
    estado = models.CharField('Estado', max_length=2, blank=True, null=True)
    
    # Informações de negócio
    interesse = models.CharField('Interesse', max_length=20, choices=INTEREST_CHOICES, default='consorcio')
    valor_interesse = models.DecimalField('Valor de Interesse', max_digits=12, decimal_places=2, blank=True, null=True)
    prazo_desejado = models.IntegerField('Prazo Desejado (meses)', blank=True, null=True)
    
    # Gestão
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='novo')
    fonte = models.CharField('Fonte', max_length=20, choices=SOURCE_CHOICES, default='site')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='leads_responsavel')
    prioridade = models.IntegerField('Prioridade', default=2, choices=PRIORITY_CHOICES)
    observacoes = models.TextField('Observações', blank=True, null=True)
    
    # Datas
    data_criacao = models.DateTimeField('Data de Criação', default=timezone.now)
    data_modificacao = models.DateTimeField('Última Modificação', auto_now=True)
    data_ultimo_contato = models.DateTimeField('Data do Último Contato', blank=True, null=True)
    data_proxima_acao = models.DateTimeField('Data da Próxima Ação', blank=True, null=True)
    
    # Informações de importação
    arquivo_origem = models.CharField('Arquivo de Origem', max_length=255, blank=True, null=True)
    importado_em = models.DateTimeField('Importado em', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['interesse']),
            models.Index(fields=['data_criacao']),
            models.Index(fields=['responsavel']),
        ]
    
    def __str__(self):
        if self.empresa:
            return f"{self.nome} - {self.empresa}"
        return self.nome
    
    @property
    def contato_principal(self):
        """Retorna o contato principal (WhatsApp se disponível, senão telefone)."""
        return self.whatsapp or self.telefone
    
    @property
    def endereco_completo(self):
        """Retorna o endereço completo formatado."""
        partes = [
            self.logradouro,
            self.numero,
            self.complemento,
            self.bairro,
            self.cidade,
            self.estado
        ]
        return ', '.join([p for p in partes if p])


class TemplateComunitacao(models.Model):
    """Template base para comunicações."""
    
    TIPO_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'E-mail'),
        ('sms', 'SMS'),
    ]
    
    nome = models.CharField('Nome', max_length=100)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    assunto = models.CharField('Assunto', max_length=200, blank=True, null=True)
    conteudo = models.TextField('Conteúdo')
    ativo = models.BooleanField('Ativo', default=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Template de Comunicação'
        verbose_name_plural = 'Templates de Comunicação'
        ordering = ['tipo', 'nome']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome}"


class HistoricoContato(models.Model):
    """Histórico de contatos realizados com leads."""
    
    TIPO_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'E-mail'),
        ('telefone', 'Telefone'),
        ('sms', 'SMS'),
        ('reuniao', 'Reunião'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('lido', 'Lido'),
        ('respondido', 'Respondido'),
        ('erro', 'Erro'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='historico_contatos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    assunto = models.CharField('Assunto', max_length=200, blank=True, null=True)
    mensagem = models.TextField('Mensagem')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='enviado')
    data_envio = models.DateTimeField('Data de Envio', auto_now_add=True)
    data_resposta = models.DateTimeField('Data da Resposta', blank=True, null=True)
    template_usado = models.ForeignKey(TemplateComunitacao, on_delete=models.SET_NULL, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Histórico de Contato'
        verbose_name_plural = 'Histórico de Contatos'
        ordering = ['-data_envio']
    
    def __str__(self):
        return f"{self.lead.nome} - {self.get_tipo_display()} em {self.data_envio.strftime('%d/%m/%Y %H:%M')}"
