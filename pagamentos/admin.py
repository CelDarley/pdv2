from django.contrib import admin
from .models import Pagamento

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'forma_pagamento', 'valor', 'troco', 'data']
    list_filter = ['forma_pagamento', 'data']
    search_fields = ['pedido__id', 'forma_pagamento']
    readonly_fields = ['data']
