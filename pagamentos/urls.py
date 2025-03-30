from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pagamentos, name='lista_pagamentos'),
    path('novo/', views.novo_pagamento, name='novo_pagamento'),
    path('editar/<int:pk>/', views.editar_pagamento, name='editar_pagamento'),
    path('excluir/<int:pk>/', views.excluir_pagamento, name='excluir_pagamento'),
] 