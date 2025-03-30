from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.index, name='index'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('adicionar-ao-pedido/', views.adicionar_ao_pedido, name='adicionar_ao_pedido'),
    path('remover-item/<int:index>/', views.remover_item, name='remover_item'),
    path('finalizar-pedido/', views.finalizar_pedido, name='finalizar_pedido'),
    path('pagamento/<int:pedido_id>/', views.pagamento, name='pagamento'),
    path('processar-pagamento/<int:pedido_id>/', views.processar_pagamento, name='processar_pagamento'),
    path('listar-pedidos/', views.listar_pedidos, name='listar_pedidos'),
] 