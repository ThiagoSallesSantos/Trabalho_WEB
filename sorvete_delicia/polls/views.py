from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
from sorvete_delicia.settings import MEDIA_ROOT

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

## Paginas Auxiliares - Acesso ao Banco

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