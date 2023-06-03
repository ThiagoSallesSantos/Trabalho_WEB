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
        SQL = "SELECT * FROM polls_sorvete"
        cursor.execute(SQL)
        lista_sorvetes = dictfetchall(cursor)
    return render(request, "index.html", {"lista_sorvetes": lista_sorvetes})

def imageExportView(request, name):
        imagem_file = MEDIA_ROOT+"/"+name
        image_data = open(imagem_file, "rb").read()
        return HttpResponse(image_data, content_type="image/png")