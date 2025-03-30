from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('preco_unitario',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'data_pedido', 'status', 'valor_total')
    list_filter = ('status', 'forma_pagamento')
    search_fields = ('cliente__username',)
    inlines = [ItemPedidoInline]
    readonly_fields = ('valor_total',)
