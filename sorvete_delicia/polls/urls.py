from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sorvete/<int:id_sorvete>", views.sorvete, name="sorvete"),
    path("exibir_imagem/<str:path_imagem>", views.exibir_imagem, name="exibir_imagem")
]