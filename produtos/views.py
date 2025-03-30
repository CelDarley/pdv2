from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Produto, Extra, Categoria
from .serializers import ProdutoSerializer, ExtraSerializer
from django.contrib import messages
from pedidos.models import Pedido, ItemPedido
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@login_required
def index(request):
    produtos = Produto.objects.all()
    pedido_atual = request.session.get('pedido_atual')
    pedidos_anteriores = Pedido.objects.all().order_by('-data_pedido')[:5]
    
    # Se não houver pedido atual, inicializa um vazio
    if not pedido_atual:
        pedido_atual = {
            'itens': [],
            'total': 0
        }
        request.session['pedido_atual'] = pedido_atual
    
    return render(request, 'produtos/index.html', {
        'produtos': produtos,
        'pedido_atual': pedido_atual,
        'pedidos_anteriores': pedidos_anteriores
    })

@login_required
@require_http_methods(["POST"])
def adicionar_ao_pedido(request):
    try:
        # Lê os dados JSON da requisição
        dados = json.loads(request.body)
        print("Dados recebidos:", dados)
        produto_id = dados.get('produto_id')
        quantidade = dados.get('quantidade', 1)
        extras = dados.get('extras', [])
        print("Produto ID:", produto_id)
        print("Quantidade:", quantidade)
        print("Extras:", extras)

        # Obtém o produto
        produto = get_object_or_404(Produto, id=produto_id)
        print("Produto encontrado:", produto)

        # Obtém ou cria o pedido atual
        pedido_atual, criado = Pedido.objects.get_or_create(
            cliente=request.user,
            status='Em preparação',
            defaults={'valor_total': 0}
        )
        print("Pedido atual:", pedido_atual, "Criado:", criado)

        # Cria o item do pedido
        item = ItemPedido.objects.create(
            pedido=pedido_atual,
            produto=produto,
            quantidade=quantidade,
            preco_unitario=produto.preco
        )
        print("Item criado:", item)

        # Adiciona os extras
        for extra_id in extras:
            extra = Extra.objects.get(id=extra_id)
            item.extras.add(extra)
            print("Extra adicionado:", extra)

        # Calcula o preço total do item
        preco_total = item.preco_unitario * item.quantidade
        for extra in item.extras.all():
            preco_total += extra.preco * item.quantidade
        print("Preço total do item:", preco_total)

        # Atualiza o total do pedido
        pedido_atual.valor_total += preco_total
        pedido_atual.save()
        print("Total do pedido atualizado:", pedido_atual.valor_total)

        # Prepara os nomes dos extras
        extras_nomes = [extra.nome for extra in item.extras.all()]

        return JsonResponse({
            'success': True,
            'message': 'Produto adicionado com sucesso!',
            'pedido_id': pedido_atual.id,
            'total': float(pedido_atual.valor_total),
            'item': {
                'produto_nome': produto.nome,
                'quantidade': quantidade,
                'preco_unitario': float(produto.preco),
                'preco_total': float(preco_total),
                'extras': extras_nomes
            }
        })
    except json.JSONDecodeError as e:
        print("Erro ao decodificar JSON:", str(e))
        return JsonResponse({
            'success': False,
            'error': 'Dados inválidos'
        }, status=400)
    except Exception as e:
        print("Erro ao adicionar produto:", str(e))
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def remover_item(request, indice):
    pedido_atual = Pedido.objects.filter(cliente=request.user, status='Em preparação').first()
    if pedido_atual and 0 <= indice < len(pedido_atual.itens):
        item = pedido_atual.itens[indice]
        pedido_atual.total -= item.preco_total
        pedido_atual.save()
        item.delete()
        messages.success(request, 'Item removido com sucesso!')
    return redirect('produtos:index')

@login_required
def finalizar_pedido(request):
    pedido_atual = Pedido.objects.filter(cliente=request.user, status='Em preparação').first()
    if pedido_atual:
        pedido_atual.status = 'Aguardando pagamento'
        pedido_atual.save()
        messages.success(request, 'Pedido finalizado com sucesso!')
    return redirect('produtos:index')

# Create your views here.

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.filter(disponivel=True)
    serializer_class = ProdutoSerializer
    permission_classes = [AllowAny]  # Permite acesso público à lista de produtos
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

class ExtraViewSet(viewsets.ModelViewSet):
    queryset = Extra.objects.all()
    serializer_class = ExtraSerializer
    permission_classes = [AllowAny]  # Permite acesso público à lista de extras
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
