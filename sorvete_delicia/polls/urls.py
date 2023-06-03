from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("image/<str:name>", views.imageExportView, name="image"),
]