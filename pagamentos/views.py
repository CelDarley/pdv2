from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Pagamento
from .serializers import PagamentoSerializer
import qrcode
from io import BytesIO
from django.core.files import File
from django.contrib import messages
from pedidos.models import Pedido

# Create your views here.

class PagamentoViewSet(viewsets.ModelViewSet):
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Pagamento.objects.filter(pedido__cliente=self.request.user)
    
    def perform_create(self, serializer):
        pagamento = serializer.save()
        if pagamento.pedido.forma_pagamento == 'pix':
            self.gerar_qr_code(pagamento)
    
    @action(detail=True, methods=['post'])
    def processar_pagamento(self, request, pk=None):
        pagamento = self.get_object()
        tipo_pagamento = request.data.get('tipo')
        valor_recebido = request.data.get('valor_recebido', 0)
        
        if tipo_pagamento == 'cartao':
            # Simula processamento do cartão
            pagamento.status = 'aprovado'
            pagamento.save()
            return Response({'status': 'Pagamento aprovado'})
            
        elif tipo_pagamento == 'pix':
            # Simula confirmação do PIX
            pagamento.status = 'aprovado'
            pagamento.save()
            return Response({'status': 'Pagamento PIX confirmado'})
            
        elif tipo_pagamento == 'dinheiro':
            if float(valor_recebido) >= float(pagamento.valor):
                troco = float(valor_recebido) - float(pagamento.valor)
                pagamento.status = 'aprovado'
                pagamento.save()
                return Response({
                    'status': 'Pagamento aprovado',
                    'troco': f'{troco:.2f}'
                })
            else:
                return Response(
                    {'error': 'Valor insuficiente'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {'error': 'Tipo de pagamento inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def gerar_qr_code(self, pagamento):
        # Gera um QR Code para pagamento PIX (simulação)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f'PIX_SIMULADO_{pagamento.id}_{pagamento.valor}')
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Salva o QR Code
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_code_pedido_{pagamento.pedido.id}.png'
        pagamento.qr_code.save(filename, File(buffer), save=True)

def lista_pagamentos(request):
    pagamentos = Pagamento.objects.all().order_by('-data')
    return render(request, 'pagamentos/lista.html', {'pagamentos': pagamentos})

def novo_pagamento(request):
    if request.method == 'POST':
        try:
            pagamento = Pagamento.objects.create(
                pedido_id=request.POST.get('pedido_id'),
                forma_pagamento=request.POST.get('forma_pagamento'),
                valor=request.POST.get('valor'),
                troco=request.POST.get('troco', 0)
            )
            messages.success(request, 'Pagamento registrado com sucesso!')
            return redirect('lista_pagamentos')
        except Exception as e:
            messages.error(request, f'Erro ao registrar pagamento: {str(e)}')
    
    pedidos = Pedido.objects.filter(status='Em preparação')
    return render(request, 'pagamentos/novo.html', {'pedidos': pedidos})

def editar_pagamento(request, pk):
    pagamento = get_object_or_404(Pagamento, pk=pk)
    if request.method == 'POST':
        try:
            pagamento.forma_pagamento = request.POST.get('forma_pagamento')
            pagamento.valor = request.POST.get('valor')
            pagamento.troco = request.POST.get('troco', 0)
            pagamento.save()
            messages.success(request, 'Pagamento atualizado com sucesso!')
            return redirect('lista_pagamentos')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar pagamento: {str(e)}')
    return render(request, 'pagamentos/editar.html', {'pagamento': pagamento})

def excluir_pagamento(request, pk):
    pagamento = get_object_or_404(Pagamento, pk=pk)
    if request.method == 'POST':
        try:
            pagamento.delete()
            messages.success(request, 'Pagamento excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir pagamento: {str(e)}')
    return redirect('lista_pagamentos')
