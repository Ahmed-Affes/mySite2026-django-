"""
magasin/admin.py  —  Register all models in the Django admin panel
"""

from django.contrib import admin
from .models import Produit, Categorie, Fournisseur, Commande


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name')
    search_fields = ('name',)


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nom', 'email', 'telephone', 'adresse')
    search_fields = ('nom', 'email')


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display   = ('id', 'libelle', 'type', 'prix', 'categorie', 'fournisseur')
    list_filter    = ('type', 'categorie', 'fournisseur')
    search_fields  = ('libelle', 'description')
    list_per_page  = 25
    raw_id_fields  = ('fournisseur',)


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display  = ('id', 'totalCde', 'dateCde')
    list_filter   = ('dateCde',)
    filter_horizontal = ('produits',)
    date_hierarchy = 'dateCde'