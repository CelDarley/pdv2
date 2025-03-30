from rest_framework import serializers
from .models import Pedido, ItemPedido
from produtos.serializers import ProdutoSerializer, ExtraSerializer

class ItemPedidoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    produto_id = serializers.IntegerField(write_only=True)
    extras = ExtraSerializer(many=True, read_only=True)
    extras_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ItemPedido
        fields = ['id', 'produto', 'produto_id', 'quantidade', 'preco_unitario', 'extras', 'extras_ids']
        read_only_fields = ['preco_unitario']

    def create(self, validated_data):
        extras_ids = validated_data.pop('extras_ids', [])
        item = ItemPedido.objects.create(**validated_data)
        if extras_ids:
            item.extras.set(extras_ids)
        return item

class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'data_pedido', 'status', 'forma_pagamento', 
                 'valor_total', 'troco', 'itens']
        read_only_fields = ['cliente', 'data_pedido', 'valor_total']

    def create(self, validated_data):
        validated_data['cliente'] = self.context['request'].user
        return super().create(validated_data) 