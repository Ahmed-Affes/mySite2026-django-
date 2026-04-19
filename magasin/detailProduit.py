
from sys import path

from django import views
from django.shortcuts import render
from .models import Produit, Categorie
path('produit/<int:id>/', views.detailProduit, name='detail')