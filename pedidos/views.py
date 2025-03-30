from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from .models import Pedido, ItemPedido
from .serializers import PedidoSerializer, ItemPedidoSerializer
from produtos.models import Produto, Extra
from pagamentos.models import Pagamento
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from decimal import Decimal
from datetime import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.

def carrinho(request):
    pedido_atual = request.session.get('pedido_atual', None)
    pedidos_anteriores = Pedido.objects.all().order_by('-data_pedido')[:5]
    return render(request, 'pedidos/carrinho.html', {
        'pedido_atual': pedido_atual,
        'pedidos_anteriores': pedidos_anteriores
    })

def adicionar_ao_pedido(request):
    if request.method == 'POST':
        try:
            print("=== Iniciando processamento de adicionar_ao_pedido ===")  # Debug
            print(f"Headers da requisição: {dict(request.headers)}")  # Debug
            
            # Obtém os dados JSON do corpo da requisição
            body = request.body.decode('utf-8')
            print(f"Corpo da requisição: {body}")  # Debug
            
            data = json.loads(body)
            print(f"Dados recebidos: {data}")  # Debug
            
            produto_id = data.get('produto_id')
            quantidade = int(data.get('quantidade', 1))
            extras = data.get('extras', [])

            print(f"Produto ID: {produto_id}")  # Debug
            print(f"Quantidade: {quantidade}")  # Debug
            print(f"Extras: {extras}")  # Debug

            produto = Produto.objects.get(id=produto_id)
            print(f"Produto encontrado: {produto.nome}")  # Debug
            
            # Cria ou obtém o pedido atual da sessão
            pedido_atual = request.session.get('pedido_atual', {
                'itens': [],
                'total': 0
            })
            print(f"Pedido atual na sessão: {pedido_atual}")  # Debug

            # Calcula o preço total do item
            preco_total = produto.preco * quantidade
            for extra in extras:
                if extra == 'Molho Especial':
                    preco_total += 2.00 * quantidade
                elif extra in ['Ketchup', 'Maionese']:
                    preco_total += 1.50 * quantidade

            print(f"Preço total calculado: {preco_total}")  # Debug

            # Adiciona o item ao pedido
            item = {
                'produto': {
                    'id': produto.id,
                    'nome': produto.nome,
                    'preco': float(produto.preco),
                    'imagem': produto.imagem.url if produto.imagem else None
                },
                'quantidade': quantidade,
                'extras': extras,
                'preco_total': float(preco_total)
            }
            
            pedido_atual['itens'].append(item)
            pedido_atual['total'] = float(sum(item['preco_total'] for item in pedido_atual['itens']))
            
            print(f"Item a ser adicionado: {item}")  # Debug
            print(f"Total atualizado: {pedido_atual['total']}")  # Debug
            
            request.session['pedido_atual'] = pedido_atual
            print("Pedido atual salvo na sessão")  # Debug
            
            response_data = {
                'success': True,
                'item': item,
                'total': pedido_atual['total']
            }
            print(f"Resposta a ser enviada: {response_data}")  # Debug
            
            return JsonResponse(response_data)
            
        except Produto.DoesNotExist:
            print(f"Produto não encontrado com ID: {produto_id}")  # Debug
            return JsonResponse({
                'success': False,
                'error': 'Produto não encontrado.'
            })
        except Exception as e:
            print(f"Erro ao adicionar ao pedido: {str(e)}")  # Debug
            print(f"Stack trace: {e.__traceback__}")  # Debug
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

def remover_item(request, index):
    if request.method == 'POST':
        pedido_atual = request.session.get('pedido_atual')
        if pedido_atual and 0 <= index < len(pedido_atual['itens']):
            pedido_atual['itens'].pop(index)
            pedido_atual['total'] = sum(item['preco_total'] for item in pedido_atual['itens'])
            request.session['pedido_atual'] = pedido_atual
            messages.success(request, 'Item removido do pedido com sucesso!')
        return redirect('carrinho')

def finalizar_pedido(request):
    if request.method == 'POST':
        pedido_atual = request.session.get('pedido_atual')
        print(f"Pedido atual na sessão: {pedido_atual}")  # Debug
        
        if pedido_atual and 'itens' in pedido_atual and pedido_atual['itens']:
            try:
                print(f"Itens do pedido: {pedido_atual['itens']}")  # Debug
                # Cria o pedido no banco de dados
                pedido = Pedido.objects.create(
                    cliente=request.user,
                    data_pedido=timezone.now(),
                    status='em_preparacao',
                    valor_total=pedido_atual['total']
                )
                print(f"Pedido criado com ID: {pedido.id}")  # Debug

                # Adiciona os itens ao pedido
                for item in pedido_atual['itens']:
                    print(f"Processando item: {item}")  # Debug
                    produto = Produto.objects.get(id=item['produto']['id'])
                    item_pedido = ItemPedido.objects.create(
                        pedido=pedido,
                        produto=produto,
                        quantidade=item['quantidade'],
                        preco_unitario=produto.preco
                    )
                    # Adiciona os extras ao item
                    for extra_nome in item['extras']:
                        extra = Extra.objects.get(nome=extra_nome)
                        item_pedido.extras.add(extra)
                    print(f"Item criado para o produto: {produto.nome}")  # Debug

                # Limpa o pedido atual da sessão
                del request.session['pedido_atual']
                print("Pedido atual removido da sessão")  # Debug

                # Retorna os dados do pedido criado
                return JsonResponse({
                    'success': True,
                    'pedido': {
                        'id': pedido.id,
                        'data_pedido': pedido.data_pedido.strftime('%H:%M'),
                        'total': float(pedido.valor_total)
                    }
                })
            except Exception as e:
                print(f"Erro ao processar pedido: {str(e)}")  # Debug
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao processar pedido: {str(e)}'
                })
        
        print(f"Pedido atual inválido ou vazio: {pedido_atual}")  # Debug
        return JsonResponse({
            'success': False,
            'error': 'Nenhum item no pedido atual'
        })

def pagamento(request, pedido_id):
    if request.method == 'POST':
        try:
            # Obtém todos os IDs dos pedidos
            pedidos_ids = request.POST.get('pedidos_ids', '').split(',')
            pedidos_ids = [int(pid) for pid in pedidos_ids if pid.isdigit()]
            
            # Obtém o total geral
            total_geral = float(request.POST.get('total_geral', 0))
            
            # Busca todos os pedidos
            pedidos = Pedido.objects.filter(id__in=pedidos_ids, cliente=request.user, ativo=True)
            
            # Verifica se todos os pedidos foram encontrados
            if len(pedidos) != len(pedidos_ids):
                messages.error(request, 'Alguns pedidos não foram encontrados.')
                return redirect('produtos:index')
            
            # Verifica se o total geral está correto
            total_calculado = sum(float(p.valor_total) for p in pedidos)
            if abs(total_calculado - total_geral) > 0.01:  # Permite uma pequena diferença de arredondamento
                messages.error(request, 'O total geral está incorreto.')
                return redirect('produtos:index')
            
            return render(request, 'pedidos/pagamento.html', {
                'pedidos': pedidos,
                'total_geral': total_geral
            })
        except Exception as e:
            messages.error(request, f'Erro ao processar pagamento: {str(e)}')
            return redirect('produtos:index')
    else:
        # Para requisições GET, mostra apenas o pedido específico
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
        return render(request, 'pedidos/pagamento.html', {
            'pedidos': [pedido],
            'total_geral': float(pedido.valor_total)
        })

@login_required
def processar_pagamento(request, pedido_id):
    if request.method == 'POST':
        try:
            # Busca todos os pedidos ativos do usuário
            pedidos = Pedido.objects.filter(cliente=request.user, ativo=True)
            forma_pagamento = request.POST.get('forma_pagamento')
            
            if forma_pagamento in ['cartao', 'pix']:
                # Marca todos os pedidos como pagos e inativos
                pedidos.update(
                    forma_pagamento=forma_pagamento,
                    status='pago',
                    ativo=False
                )
                
                messages.success(request, 'Pagamento processado com sucesso!')
            else:
                messages.error(request, 'Forma de pagamento inválida.')
        except Exception as e:
            messages.error(request, f'Erro ao processar pagamento: {str(e)}')
    
    return redirect('produtos:index')

class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Pedido.objects.filter(cliente=self.request.user)
    
    @action(detail=True, methods=['post'])
    def adicionar_item(self, request, pk=None):
        pedido = self.get_object()
        serializer = ItemPedidoSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(pedido=pedido)
            # Recalcula o valor total do pedido
            valor_total = pedido.itens.aggregate(
                total=Sum('preco_unitario')
            )['total'] or 0
            pedido.valor_total = valor_total
            pedido.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remover_item(self, request, pk=None):
        pedido = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            item = pedido.itens.get(id=item_id)
            item.delete()
            
            # Recalcula o valor total do pedido
            valor_total = pedido.itens.aggregate(
                total=Sum('preco_unitario')
            )['total'] or 0
            pedido.valor_total = valor_total
            pedido.save()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ItemPedido.DoesNotExist:
            return Response(
                {'error': 'Item não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def atualizar_status(self, request, pk=None):
        pedido = self.get_object()
        novo_status = request.data.get('status')
        
        if novo_status in dict(Pedido.STATUS_CHOICES):
            pedido.status = novo_status
            pedido.save()
            return Response({'status': 'success'})
        return Response(
            {'error': 'Status inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )

@login_required
def listar_pedidos(request):
    """View para listar os pedidos do usuário"""
    if request.method == 'POST':
        try:
            # Busca apenas pedidos ativos e não pagos do usuário atual
            pedidos = Pedido.objects.filter(
                cliente=request.user,
                ativo=True,
                status__in=['em_preparacao', 'pronto']
            ).exclude(
                status='pago'
            ).order_by('-data_pedido')
            
            pedidos_data = []
            for pedido in pedidos:
                pedido_dict = {
                    'id': pedido.id,
                    'data': pedido.data_pedido.strftime('%H:%M'),
                    'valor_total': float(pedido.valor_total),
                    'status': pedido.status,
                    'forma_pagamento': pedido.forma_pagamento,
                    'itens': []
                }
                
                for item in pedido.itens.all():
                    pedido_dict['itens'].append({
                        'produto': item.produto.nome,
                        'quantidade': item.quantidade,
                        'preco_unitario': float(item.preco_unitario),
                        'preco_total': float(item.preco_total)
                    })
                pedidos_data.append(pedido_dict)
            
            return JsonResponse({'pedidos': pedidos_data})
        except Exception as e:
            print(f"Erro ao listar pedidos: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método não permitido'}, status=405)

def index(request):
    """View para exibir a página inicial dos pedidos"""
    produtos = Produto.objects.all()
    # Busca apenas pedidos ativos e não pagos do cliente atual
    pedidos_anteriores = Pedido.objects.filter(
        cliente=request.user,
        ativo=True,
        status__in=['em_preparacao', 'pronto']
    ).exclude(
        status='pago'
    ).order_by('-data_pedido')[:5]
    
    return render(request, 'pedidos/index.html', {
        'produtos': produtos,
        'pedidos_anteriores': pedidos_anteriores
    })
