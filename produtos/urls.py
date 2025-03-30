from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.index, name='index'),
    path('adicionar-ao-pedido/', views.adicionar_ao_pedido, name='adicionar_ao_pedido'),
] 