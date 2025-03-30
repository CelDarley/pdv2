from django.db import models
from django.contrib.auth.models import User
from produtos.models import Produto, Extra

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('em_preparacao', 'Em preparação'),
        ('pronto', 'Pronto'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('cartao', 'Cartão de Crédito/Débito'),
        ('pix', 'PIX'),
        ('dinheiro', 'Dinheiro'),
    ]
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    troco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username} - {self.data_pedido.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_pedido']

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    extras = models.ManyToManyField(Extra, blank=True)
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)

    @property
    def preco_total(self):
        total = self.preco_unitario * self.quantidade
        for extra in self.extras.all():
            total += extra.preco * self.quantidade
        return total
