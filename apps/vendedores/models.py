"""
Modelos consolidados para a aplicação vendedores.
Inclui TentativaContato, Evento e Nota.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date


class TentativaContato(models.Model):
    """
    Modelo para registrar tentativas de contato com leads.
    Cada lead deve ser contatada apenas uma vez a cada 3 dias
    pelo mesmo vendedor.
    """
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE, related_name='tentativas_contato')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tentativas_contato')
    data_hora = models.DateTimeField(auto_now_add=True)
    resultado = models.CharField(
        max_length=20,
        choices=[
            ('sucesso', 'Contato realizado com sucesso'),
            ('nao_atendeu', 'Não atendeu'),
            ('ocupado', 'Ocupado/Indisponível'),
            ('numero_invalido', 'Número inválido'),
            ('outro', 'Outro motivo'),
        ],
        default='nao_atendeu'
    )
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Tentativa de contato"
        verbose_name_plural = "Tentativas de contato"
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['lead', 'vendedor', '-data_hora']),
            models.Index(fields=['lead', '-data_hora']),
            models.Index(fields=['vendedor', '-data_hora']),
        ]
    
    def __str__(self):
        return f"{self.lead.nome} - {self.vendedor.username} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

    @classmethod
    def pode_contatar(cls, lead, vendedor):
        """
        Verifica se um vendedor pode contatar uma lead específica.
        Regra: Uma tentativa por vendedor a cada 3 dias para a mesma lead.
        """
        tres_dias_atras = timezone.now() - timedelta(days=3)
        
        return not cls.objects.filter(
            lead=lead,
            vendedor=vendedor,
            data_hora__gt=tres_dias_atras
        ).exists()
    
    @classmethod
    def foi_contatado_recentemente(cls, lead):
        """
        Verifica se a lead foi contatada por qualquer vendedor recentemente.
        Retorna True se houve contato nos últimos 3 dias.
        """
        tres_dias_atras = timezone.now() - timedelta(days=3)
        return cls.objects.filter(
            lead=lead, 
            data_hora__gt=tres_dias_atras
        ).exists()


class Evento(models.Model):
    """
    Modelo para eventos e compromissos do vendedor.
    Permite agendar reuniões, contatos e prazos importantes.
    """
    TIPOS_EVENTO = [
        ('reuniao', 'Reunião'),
        ('prazo', 'Prazo/Deadline'),
        ('contato', 'Contato com Lead'),
        ('outro', 'Outro'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    data = models.DateField()
    hora = models.TimeField()
    tipo = models.CharField(max_length=20, choices=TIPOS_EVENTO)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos')
    lead = models.ForeignKey(
        'leads.Lead', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='eventos'
    )
    concluido = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['data', 'hora']
        indexes = [
            models.Index(fields=['vendedor', 'data', 'hora']),
            models.Index(fields=['data', 'concluido']),
            models.Index(fields=['vendedor', 'concluido']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.data.strftime('%d/%m/%Y')}"
    
    @property
    def esta_proximo(self):
        """Verifica se o evento está para acontecer nos próximos 2 dias."""
        hoje = date.today()
        return (self.data - hoje).days <= 2 and (self.data - hoje).days >= 0
        
    @property
    def esta_atrasado(self):
        """Verifica se o evento já passou e não foi concluído."""
        hoje = date.today()
        return self.data < hoje and not self.concluido
        
    @classmethod
    def proximos_eventos(cls, vendedor, dias=7):
        """Retorna eventos próximos para o vendedor."""
        hoje = date.today()
        return cls.objects.filter(
            vendedor=vendedor,
            data__gte=hoje,
            data__lte=hoje + timedelta(days=dias),
            concluido=False
        ).order_by('data', 'hora')


class Nota(models.Model):
    """
    Modelo para notas e lembretes dos vendedores.
    """
    PRIORIDADE_CHOICES = [
        (1, 'Baixa'),
        (2, 'Média'),
        (3, 'Alta'),
    ]
    
    TIPO_CHOICES = [
        ('nota', 'Nota'),
        ('lembrete', 'Lembrete'),
    ]
    
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notas')
    lead = models.ForeignKey(
        'leads.Lead', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notas'
    )
    prioridade = models.IntegerField(choices=PRIORIDADE_CHOICES, default=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='nota')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    concluido = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        ordering = ['-prioridade', '-data_criacao']
        indexes = [
            models.Index(fields=['vendedor', 'concluido', '-prioridade']),
            models.Index(fields=['tipo', 'concluido']),
            models.Index(fields=['lead', 'vendedor']),
        ]
        
    def __str__(self):
        return self.titulo
        
    @property
    def get_prioridade_display_css(self):
        """Retorna a classe CSS para estilização baseada na prioridade."""
        return {3: 'alta', 2: 'media', 1: 'baixa'}[self.prioridade]
            
    def save(self, *args, **kwargs):
        """Salva a nota e registra data de conclusão se for concluída."""
        if self.concluido and not self.data_conclusao:
            self.data_conclusao = timezone.now()
        elif not self.concluido:
            self.data_conclusao = None
        super().save(*args, **kwargs)
    
    @classmethod
    def lembretes_ativos(cls, vendedor):
        """Retorna lembretes ativos (não concluídos) para o vendedor."""
        return cls.objects.filter(
            vendedor=vendedor,
            concluido=False,
            tipo='lembrete'
        ).order_by('-prioridade', '-data_criacao')