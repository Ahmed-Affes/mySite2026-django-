"""
magasin/urls.py  —  Enterprise URL patterns
"""

from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/',  views.profile_view,  name='profile'),

    path('',          views.home_view,     name='home'),

    # Products
    path('catalogue/',         views.index,  name='index'),
    path('produit/<int:pk>/',  views.detail, name='detail'),
    path('produit/add/',       views.produit_create, name='produit_create'),
    path('produit/<int:pk>/edit/', views.produit_edit, name='produit_edit'),
    path('produit/<int:pk>/delete/', views.produit_delete, name='produit_delete'),
    path('produit/<int:pk>/sources/', views.produit_sources_manage, name='produit_sources_manage'),
    path('produit/<int:pk>/avis/', views.review_add, name='review_add'),

    # Admin Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Suppliers
    path('fournisseurs/',                     views.FournisseurListView.as_view(),   name='fournisseurs'),
    path('fournisseurs/add/',                 views.FournisseurCreateView.as_view(), name='fournisseur_create'),
    path('fournisseurs/<int:pk>/detail/',     views.FournisseurDetailView.as_view(),  name='fournisseur_detail'),
    path('fournisseurs/<int:pk>/edit/',       views.FournisseurUpdateView.as_view(),   name='fournisseur_edit'),
    path('fournisseurs/<int:pk>/delete/',     views.FournisseurDeleteView.as_view(), name='fournisseur_delete'),

    # Cart
    path('panier/',                           views.panier_voir,      name='panier_voir'),
    path('panier/ajouter/<int:pk>/',          views.panier_ajouter,   name='panier_ajouter'),
    path('panier/diminuer/<int:pk>/',         views.panier_diminuer,  name='panier_diminuer'),
    path('panier/supprimer/<int:pk>/',        views.panier_supprimer, name='panier_supprimer'),
    path('panier/vider/',                     views.panier_vider,     name='panier_vider'),
    path('panier/commander/',                 views.panier_commander, name='panier_commander'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/ajouter/<int:pk>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/supprimer/<int:pk>/', views.wishlist_remove, name='wishlist_remove'),

    # Orders (Client)
    path('commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:pk>/annuler/', views.client_annuler_commande, name='client_annuler_commande'),

    # Orders (Admin)
    path('commandes/toutes/', views.toutes_commandes, name='toutes_commandes'),
    path('commande/<int:pk>/', views.commande_detail, name='commande_detail'),
    path('commande/<int:pk>/update-status/', views.update_commande_status, name='update_commande_status'),
    path('commande/<int:pk>/generer-bdc/', views.commande_generer_bdc, name='commande_generer_bdc'),

    # Purchase Orders (BDC)
    path('bdc/', views.bdc_liste, name='bdc_liste'),
    path('bdc/nouveau/', views.bdc_create, name='bdc_create'),
    path('bdc/<int:pk>/status/<str:status>/', views.bdc_status_update, name='bdc_status_update'),
    path('bdc/<int:pk>/imprimer/', views.bdc_print, name='bdc_print'),

    # Notifications
    path('notifications/', views.notifications_liste, name='notifications'),
]