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
    print(f"Teste: {MEDIA_ROOT}")
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
                                            "lista_tigelas": get_all_tigelas(),
                                            "lista_componentes": get_all_componentes()
                                        })

## Paginas Auxiliares

def get_all_componentes():
    lista_componentes = list([])
    with connection.cursor() as cursor:
        SQL = """
            SELECT *
            FROM polls_componente;
        """
        cursor.execute(SQL)
        lista_componentes = dictfetchall(cursor)
        print(lista_componentes)
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
        print(lista_tigelas)
    return lista_tigelas

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

def exibir_imagem(request, path_imagem):
    imagem_file = MEDIA_ROOT+"/"+path_imagem
    image_data = open(imagem_file, "rb").read()
    return HttpResponse(image_data, content_type="image/png")