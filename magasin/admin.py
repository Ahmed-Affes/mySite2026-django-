"""
magasin/admin.py  —  Enterprise Admin configuration
"""

from django.contrib import admin
from .models import (
    Produit, Categorie, Fournisseur, Commande, CommandeLigne, 
    Wishlist, Review, BonDeCommande, BonDeCommandeLigne, Notification,
    ProduitFournisseur
)

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'email', 'telephone', 'adresse')
    search_fields = ('nom', 'email')

class ProduitFournisseurInline(admin.TabularInline):
    model = ProduitFournisseur
    extra = 1

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('id', 'libelle', 'type', 'prix', 'stock', 'stock_minimum', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('libelle', 'description')
    list_editable = ('stock', 'stock_minimum', 'is_active')
    inlines = [ProduitFournisseurInline]

class CommandeLigneInline(admin.TabularInline):
    model = CommandeLigne
    extra = 0
    readonly_fields = ('sous_total',)

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'totalCde', 'dateCde')
    list_filter = ('status', 'dateCde')
    search_fields = ('id', 'client__username', 'adresse_livraison')
    inlines = [CommandeLigneInline]
    date_hierarchy = 'dateCde'

class BonDeCommandeLigneInline(admin.TabularInline):
    model = BonDeCommandeLigne
    extra = 1

@admin.register(BonDeCommande)
class BonDeCommandeAdmin(admin.ModelAdmin):
    list_display = ('reference', 'fournisseur', 'statut', 'date_creation')
    list_filter = ('statut', 'date_creation')
    inlines = [BonDeCommandeLigneInline]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('destinataire', 'type', 'titre', 'lu', 'cree_le')
    list_filter = ('lu', 'type')

admin.site.register(Wishlist)
admin.site.register(Review)