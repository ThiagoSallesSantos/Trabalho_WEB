from django.urls import path

from . import views

urlpatterns = [
    ## Páginas
    path("", views.index, name="index"),
    path("sorvete/<int:id_sorvete>", views.sorvete, name="sorvete"),
    path("meus_sorvetes", views.meus_sorvetes, name="meus_sorvetes"),
    path("minhas_compras", views.minhas_compras, name="minhas_compras"),
    ## Ferramentas
    path("deleta_produtos/<int:id_produto>", views.deleta_produtos, name="deleta_produtos"),
    path("exibir_imagem/<str:path_imagem>", views.exibir_imagem, name="exibir_imagem"),
    ## User
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout")
]