from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:name>", views.read, name="page"),
    path("search/", views.search, name="search"),
    path("add/", views.add, name="add"),
    path("wiki/<str:title>/edit", views.edit, name="edit"),
    path("random/", views.random_page, name="random_page")
]
