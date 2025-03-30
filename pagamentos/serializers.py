from rest_framework import serializers
from .models import Pagamento
from pedidos.serializers import PedidoSerializer

class PagamentoSerializer(serializers.ModelSerializer):
    pedido = PedidoSerializer(read_only=True)
    pedido_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Pagamento
        fields = ['id', 'pedido', 'pedido_id', 'valor', 'data_pagamento', 'status', 'qr_code']
        read_only_fields = ['data_pagamento', 'qr_code'] 