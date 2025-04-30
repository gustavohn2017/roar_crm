from django.db import models
from django.contrib.auth.models import User
from leads.models import Lead
from django.utils import timezone
from datetime import timedelta


class TentativaContato(models.Model):
    """
    Modelo para registrar tentativas de contato com leads.
    Cada lead deve ser contatada apenas uma vez a cada 3 dias
    pelo mesmo vendedor.
    """
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='tentativas_contato')
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
    
    def __str__(self):
        return f"{self.lead.nome} - {self.vendedor.username} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = "Tentativa de contato"
        verbose_name_plural = "Tentativas de contato"
        ordering = ['-data_hora']

    @classmethod
    def pode_contatar(cls, lead, vendedor):
        """
        Verifica se um vendedor pode contatar uma lead específica.
        Regra: Uma tentativa por vendedor a cada 3 dias para a mesma lead.
        """
        tres_dias_atras = timezone.now() - timedelta(days=3)
        
        # Verifica se o vendedor contatou esta lead nos últimos 3 dias
        contatos_recentes = cls.objects.filter(
            lead=lead,
            vendedor=vendedor,
            data_hora__gt=tres_dias_atras
        ).exists()
        
        return not contatos_recentes
    
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