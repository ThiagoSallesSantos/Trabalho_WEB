from django.contrib.auth.models import User
from django.db import models

class Tigela(models.Model):
    ## Tamanho de tigelas
    tigela_150ml = 150
    tigela_200ml = 200
    tigela_300ml = 300
    tigela_400ml = 400
    tigela_500ml = 500
    tigela_1L = 1000
    tamanho_tigelas = (
        (tigela_150ml, "150ml"),
        (tigela_200ml, "200ml"),
        (tigela_300ml, "300ml"),
        (tigela_400ml, "400ml"),
        (tigela_500ml, "500ml"),
        (tigela_1L, "1L"),
    )
    tamanho = models.IntegerField(choices=tamanho_tigelas)
    
    ## Tipos de tigelas
    tipo_tigela_plastico = "Plastico"
    tipo_tigela_lousa = "Lousa"
    tipo_tigela_biscoito = "Biscoito/Casquinha"
    tipo_tigela = (
        ("P", tipo_tigela_plastico),
        ("L", tipo_tigela_lousa),
        ("B", tipo_tigela_biscoito)
    )
    tipo = models.CharField(choices=tipo_tigela, max_length=1)

    def __str__(self) -> str:
        return f"Tigela: {self.tamanho} - {self.tipo}"

class Ingrediente(models.Model):
    nome = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f"{self.nome}"

class Componente(models.Model):
    nome = models.CharField(max_length=30)
    preco = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return f"{self.nome}"

class Sorvete(models.Model):
    sabor = models.CharField(max_length=30)
    marca = models.CharField(max_length=30, default=True)
    descricao = models.CharField(max_length=240, default=True)
    estoque = models.FloatField(help_text="qtd em Litros")
    preco = models.FloatField(help_text="preço em MiliLitros")
    imagem = models.ImageField(default=None)
    ingredientes = models.ManyToManyField(Ingrediente)

    def __str__(self):
        return f"{self.sabor} - {self.marca}"

class Produto(models.Model):
    componentes = models.ManyToManyField(Componente, default=True)
    tigela = models.ForeignKey(Tigela, on_delete=models.CASCADE)
    sorvete = models.ForeignKey(Sorvete, on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, default=True)

    def __str__(self) -> str:
        return f"Produto: {self.sorvete} - {self.tigela}"

class Venda(models.Model):
    produtos = models.ManyToManyField(Produto, through='RelacaoProdutoVenda')
    data = models.DateTimeField()
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, default=True)
    preco = models.FloatField(help_text="Valor em reais", default=True)

    def __str__(self) -> str:
        return f"Venda: {self.data} - {self.preco}"
    
class RelacaoProdutoVenda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE)
    qtd_produto = models.IntegerField(help_text="Quantidade do mesmo produto selecionado")

    def __str__(self) -> str:
        return f"Venda: {self.produto} (x{self.qtd_produto}) - {self.venda}"
    
