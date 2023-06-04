from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
from sorvete_delicia.settings import MEDIA_ROOT

from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm 

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


def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		print("aaaaaa")
		if form.is_valid():
			print("valido")
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
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("index")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request, "login.html", {"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("index")