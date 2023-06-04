from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sorvete/<int:id_sorvete>", views.sorvete, name="sorvete"),
    path("exibir_imagem/<str:path_imagem>", views.exibir_imagem, name="exibir_imagem"),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout")
]