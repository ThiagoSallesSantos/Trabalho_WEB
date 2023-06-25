from django.contrib import admin

from .models import *

admin.site.register(
    [Tigela, Sorvete, Ingrediente, Componente, Produto, Venda, RelacaoProdutoVenda]
)