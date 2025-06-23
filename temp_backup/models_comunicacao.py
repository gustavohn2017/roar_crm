from django.db import models
from django.utils import timezone

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
    assunto = models.CharField("Assunto", max_length=200)
    conteudo_html = models.TextField("Conteúdo HTML")
    conteudo_texto = models.TextField("Conteúdo em texto plano", blank=True, null=True)
    pode_personalizar = models.BooleanField("Permite personalização", default=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Template de E-mail"
        verbose_name_plural = "Templates de E-mail"


class HistoricoContato(models.Model):
    """Modelo para armazenar histórico de contatos com leads."""
    TIPO_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'E-mail'),
        ('telefone', 'Telefone'),
        ('reuniao', 'Reunião'),
        ('outro', 'Outro'),
    ]
    
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE, related_name='historico_contatos')
    tipo = models.CharField("Tipo de contato", max_length=20, choices=TIPO_CHOICES)
    data = models.DateTimeField("Data do contato", default=timezone.now)
    conteudo = models.TextField("Conteúdo da mensagem/conversa")
    responsavel = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='contatos_realizados')
    foi_respondido = models.BooleanField("Foi respondido", default=False)
    data_resposta = models.DateTimeField("Data da resposta", blank=True, null=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.lead.nome} - {self.data.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = "Histórico de Contato"
        verbose_name_plural = "Histórico de Contatos"
        ordering = ['-data']
