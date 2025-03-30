from django.db import models
from django.utils import timezone
from pedidos.models import Pedido

class Pagamento(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('cartao', 'Cartão de Crédito/Débito'),
        ('pix', 'PIX'),
        ('dinheiro', 'Dinheiro'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagamentos')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, default='cartao')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    troco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def __str__(self):
        return f'Pagamento #{self.id} - Pedido #{self.pedido.id}'

    class Meta:
        ordering = ['-data']
