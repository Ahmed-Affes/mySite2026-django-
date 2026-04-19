"""
magasin/urls.py  —  All URL patterns for the magasin app
"""

from django.urls import path
from . import views

urlpatterns = [

    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('register/', views.register_view, name='register'),

    path('',          views.home_view,     name='home'),

    path('catalogue/',         views.index,  name='index'),
    path('produit/<int:pk>/',  views.detail, name='detail'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('fournisseurs/',                     views.fournisseurs,      name='fournisseurs'),
    path('fournisseurs/add/',                 views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/edit/',       views.fournisseur_edit,   name='fournisseur_edit'),
    path('fournisseurs/<int:pk>/delete/',     views.fournisseur_delete, name='fournisseur_delete'),

    path('panier/',                           views.panier_voir,      name='panier_voir'),
    path('panier/ajouter/<int:pk>/',          views.panier_ajouter,   name='panier_ajouter'),
    path('panier/diminuer/<int:pk>/',         views.panier_diminuer,  name='panier_diminuer'),
    path('panier/supprimer/<int:pk>/',        views.panier_supprimer, name='panier_supprimer'),
    path('panier/vider/',                     views.panier_vider,     name='panier_vider'),
    path('panier/commander/',                 views.panier_commander, name='panier_commander'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/ajouter/<int:pk>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/supprimer/<int:pk>/', views.wishlist_remove, name='wishlist_remove'),

    path('produit/<int:pk>/avis/', views.review_add, name='review_add'),

    path('commandes/', views.mes_commandes, name='mes_commandes'),
    path('commandes/toutes/', views.toutes_commandes, name='toutes_commandes'),
    path('commande/<int:pk>/', views.commande_detail, name='commande_detail'),
    path('commande/<int:pk>/status/', views.update_commande_status, name='update_commande_status'),
    path('commande/<int:pk>/delete/', views.delete_commande, name='delete_commande'),
]