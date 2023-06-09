import pika
from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render, redirect
from django.db import connection
from sorvete_delicia.settings import MEDIA_ROOT
from .models import *
from .forms import NewUserForm, MontarSorvete, ComprarSorvete
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm 

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def index(request):
    lista_sorvetes = list([])
    with connection.cursor() as cursor:
        SQL = """
            SELECT * 
            FROM polls_sorvete;
        """
        cursor.execute(SQL)
        lista_sorvetes = dictfetchall(cursor)
    return render(request, "index.html", {"lista_sorvetes": lista_sorvetes})

def sorvete(request, id_sorvete):
    if request.method == "POST":
        form = MontarSorvete(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                cria_produto(dict(request.POST), request.user)
                messages.success(request,"Seu sorvete foi montado com sucesso!")
                return redirect("meus_sorvetes")
            else:
                messages.error(request,"Você precisar estar logado em sua conta para montar um sorvete!")
        else:
            messages.error(request,"Erro ao preencher formulário para montar o seu sorvete!")
    with connection.cursor() as cursor:
        SQL = f"""
            SELECT * 
            FROM polls_sorvete 
            WHERE id = {id_sorvete};
        """
        cursor.execute(SQL)
        sorvete = dictfetchall(cursor)[0]
    return render(request, "sorvete.html", {"sorvete": sorvete, 
                                            "lista_ingredientes": get_ingredientes_by_sorvete(id_sorvete),
                                            "lista_tigelas": organiza_lista_tigelas(get_all_tigelas()),
                                            "lista_componentes": corrigi_preco(get_all_componentes())
                                        })

def meus_sorvetes(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ComprarSorvete(request.POST)
            if form.is_valid():
                cria_venda(dict(request.POST), request.user)
                messages.success(request, "Compra encaminhada com sucessor!")
                return redirect("minhas_compras")
            else:
                messages.error(request, "Erro ao preencher formulário para comprar o seu(s) sorvete(s)!")
        return render(request, "meus_sorvetes.html", {
                                                    "lista_produtos": calcula_sorvete_disponivel(calcula_preco_produto(get_all_produtos_by_user(request.user)))
                                                })
    else:
        messages.error(request,"Você precisar estar logado em sua conta para acessar sua página de produtos!")
        return redirect("index")

def minhas_compras(request):
    if request.user.is_authenticated:
        return render(request, "minhas_compras.html", {
            "lista_vendas": get_all_vendas_by_user(request.user)
        })
    else:
        messages.error(request,"Você precisar estar logado em sua conta para acessar sua página de compra(s) passada(s)!")
        return redirect("index")

def deleta_produtos(request, id_produto: int):
    if request.user.is_authenticated:
        produto = Produto.objects.get(id=id_produto)
        if produto.cliente == request.user:
            produto.delete()
            messages.success(request,"Produto deletado com sucesso!")
        else:
            messages.error(request,"Você precisar estar logado para deletar algum produto!")
    else:
        messages.error(request,"Você precisar estar logado para deletar algum produto!")
    return redirect("meus_sorvetes")

def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("index")
		messages.error(request, form.errors)
	form = NewUserForm()
	return render(request, "register.html", {"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.success(request, f"Você foi logado com sucesso! Sr(a). {username}.")
				return redirect("index")
			else:
				messages.error(request,"A senha ou o nome de usuário está(ão) incorretos!")
		else:
			messages.error(request,"A senha ou o nome de usuário está(ão) inválidos!")
	form = AuthenticationForm()
	return render(request, "login.html", {"login_form":form})

def logout_request(request):
	logout(request)
	messages.success(request, "Você foi deslogado com sucesso") 
	return redirect("index")


## Paginas Auxiliares - Acesso ao Banco

def get_all_vendas_by_user(usuario):
    lista_vendas = Venda.objects.filter(cliente=usuario)
    for index, venda in enumerate(lista_vendas):
        venda.qtd_produto_total = 0
        lista_vendas[index].lista_produtos = venda.produtos.all()
        for index_, produto in enumerate(lista_vendas[index].lista_produtos):
            if produto:
                lista_vendas[index].lista_produtos[index_].lista_componentes = produto.componentes.all()
                lista_vendas[index].lista_produtos[index_].relacao = RelacaoProdutoVenda.objects.get(produto=produto, venda=venda)
                venda.qtd_produto_total += lista_vendas[index].lista_produtos[index_].relacao.qtd_produto
        lista_vendas[index].lista_produtos = calcula_preco_produto(lista_vendas[index].lista_produtos)
    return lista_vendas


def cria_venda(form, usuario):
    venda = Venda()
    venda.cliente = usuario
    venda.data = datetime.now()
    venda.preco = form["preco"][0]
    venda.save()

    relacao_produto_qtd = dict(zip(form["id_produto"], form["qtd_sorvete"]))
    for id_produto in relacao_produto_qtd.keys():
        if int(relacao_produto_qtd[id_produto]):
            produto = Produto.objects.get(id=id_produto)
            relacao = RelacaoProdutoVenda.objects.create(produto=produto, venda=venda, qtd_produto=relacao_produto_qtd[id_produto])
            venda.relacaoprodutovenda_set.add(relacao)
            produto.relacaoprodutovenda_set.add(relacao)
    venda.save()

    sistema_mensageria(f"Venda #{venda.id} do usuario {venda.cliente} - está em análise!")
    

def get_all_produtos_by_user(usuario):
    lista_produtos = Produto.objects.filter(cliente=usuario)
    for index, produto in enumerate(lista_produtos):
        lista_produtos[index].lista_componentes = produto.componentes.all()
    return lista_produtos

def cria_produto(form, usuario):
    produto = Produto()
    produto.tigela = Tigela.objects.get(id=form["tigela"][0])
    produto.sorvete = Sorvete.objects.get(id=form["sorvete"][0])
    produto.cliente = usuario
    produto.save()

    if "componentes" in form.keys():
        lista_componentes: list[Componente] = list([])
        for componente_id in form["componentes"]:
            lista_componentes.append(Componente.objects.get(id=componente_id))
        produto.componentes.set(lista_componentes)
        produto.save()

def get_all_componentes():
    lista_componentes = list([])
    with connection.cursor() as cursor:
        SQL = """
            SELECT *
            FROM polls_componente;
        """
        cursor.execute(SQL)
        lista_componentes = dictfetchall(cursor)
    return lista_componentes

def get_all_tigelas():
    lista_tigelas = list([])
    with connection.cursor() as cursor:
        SQL = """
            SELECT *
            FROM polls_tigela;
        """
        cursor.execute(SQL)
        lista_tigelas = dictfetchall(cursor)
    return lista_tigelas

def get_ingredientes_by_componente(id_componente):
    lista_ingredientes = list([])
    with connection.cursor() as cursor:
        SQL = f"""
            SELECT polls_ingrediente.nome
            FROM polls_ingrediente
            INNER JOIN polls_sorvete_ingredientes ON
            polls_ingrediente.id = polls_sorvete_ingredientes.ingrediente_id AND
            polls_sorvete_ingredientes.sorvete_id = {id_componente};
        """
        cursor.execute(SQL)
        lista_ingredientes = dictfetchall(cursor)
    return lista_ingredientes

def get_ingredientes_by_sorvete(id_sorvete):
    lista_ingredientes = list([])
    with connection.cursor() as cursor:
        SQL = f"""
            SELECT polls_ingrediente.nome
            FROM polls_ingrediente
            INNER JOIN polls_sorvete_ingredientes ON
            polls_ingrediente.id = polls_sorvete_ingredientes.ingrediente_id AND
            polls_sorvete_ingredientes.sorvete_id = {id_sorvete};
        """
        cursor.execute(SQL)
        lista_ingredientes = dictfetchall(cursor)
    return lista_ingredientes

## Paginas Auxiliares - Sem Acesso ao Banco

def calcula_sorvete_disponivel(lista_produtos):
    for index, produto in enumerate(lista_produtos):
        lista_produtos[index].sorvete_disponivel = int((produto.sorvete.estoque * 1000) / produto.tigela.tamanho)
    return lista_produtos

def calcula_preco_produto(lista_produtos):
    for index, produto in enumerate(lista_produtos):
        lista_produtos[index].preco = produto.sorvete.preco * produto.tigela.tamanho
        for componente in produto.lista_componentes:
            lista_produtos[index].preco += componente.preco
        lista_produtos[index].preco = f'{lista_produtos[index].preco:.2f}'
    return lista_produtos

def exibir_imagem(request, path_imagem):
    imagem_file = MEDIA_ROOT+"/"+path_imagem
    image_data = open(imagem_file, "rb").read()
    return HttpResponse(image_data, content_type="image/png")

def corrigi_preco(lista, chave="preco"):
    for index, dado in enumerate(lista):
        lista[index][chave] = f'{dado[chave]:.2f}'
    return lista

def organiza_lista_tigelas(lista_tigelas):
    lista_tigelas_organizada = dict({
        "Plastico" : dict({
            "tipo" : "Plastico",
            "tigelas" : list([])
        }),
        "Lousa" : dict({
            "tipo" : "Lousa",
            "tigelas" : list([])
        }),
        "Biscoito/Casquinha" : dict({
            "tipo" : "Biscoito/Casquinha",
            "tigelas" : list([])
        }),
        "Outros" : dict({
            "tipo" : "Outros",
            "tigelas" : list([])
        })
    })
    for dado in lista_tigelas:
        match dado["tipo"]:
            case "P":
                chave = "Plastico"
            case "L":
                chave = "Lousa"
            case "B":
                chave = "Biscoito/Casquinha"
            case _:
                chave = "Outros."
        lista_tigelas_organizada[chave]["tigelas"].append(dado)
    return list(lista_tigelas_organizada.values())

def sistema_mensageria(
        mensagem,
        user = "guest",
        password = "guest",
        host = "localhost",
        queue = "sorvete_delicia"

):
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
    exchange='',
    routing_key=queue,
    body=mensagem,
    properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
    ))
    connection.close()

