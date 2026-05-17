from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='blood_home'),
    path('connexion/', views.login_view, name='blood_login'),
    path('deconnexion/', views.logout_view, name='blood_logout'),
    path('inscription/donneur/', views.register_donneur, name='register_donneur'),
    path('inscription/hopital/', views.register_hopital, name='register_hopital'),
    path('dashboard/', views.dashboard, name='blood_dashboard'),
    path('demandes/', views.DemandeUrgenteListView.as_view(), name='blood_demandes'),
    path('demandes/nouveau/', views.DemandeUrgenteCreateView.as_view(), name='publish_request'),
    path('demandes/<int:pk>/modifier/', views.DemandeUrgenteUpdateView.as_view(), name='edit_request'),
    path('demandes/<int:pk>/supprimer/', views.DemandeUrgenteDeleteView.as_view(), name='delete_request'),
    path('demandes/<int:demande_id>/repondre/', views.respond_request, name='respond_request'),
    path('campagnes/', views.campaigns, name='blood_campaigns'),
    path('campagnes/nouveau/', views.publish_campaign, name='publish_campaign'),
    path('campagnes/<int:pk>/modifier/', views.edit_campaign, name='edit_campaign'),
    path('campagnes/<int:pk>/supprimer/', views.delete_campaign, name='delete_campaign'),
    path('campagnes/<int:campagne_id>/participer/', views.participer_campagne, name='participer_campagne'),
    path('rendezvous/tous/', views.all_rendezvous, name='all_rendezvous'),
    path('campagnes/tous/', views.all_my_campaigns, name='all_my_campaigns'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:user_id>/', views.view_conversation, name='view_conversation'),
    path('messages/<int:user_id>/supprimer/', views.delete_conversation, name='delete_conversation'),
    path('rendezvous/<int:pk>/annuler/', views.cancel_rendezvous, name='cancel_rendezvous'),
    path('rendezvous/<int:pk>/supprimer/', views.delete_rendezvous, name='delete_rendezvous'),
    path('rendezvous/<int:pk>/statut/<str:status>/', views.update_rendezvous_status, name='update_rdv_status'),
    path('reponses/<int:pk>/supprimer/', views.delete_reponse, name='delete_reponse'),
    path('don/<int:pk>/supprimer/', views.delete_don, name='delete_don'),
    path('notifications/tout-effacer/', views.clear_notifications, name='clear_notifications'),
    path('statistiques/', views.blood_statistics, name='blood_statistics'),
]

# ============================================================
# API REST FRAMEWORK - Router
# ============================================================

from django.urls import include
from rest_framework import routers
from reddrop.views import (
    DonneurViewSet, HopitalViewSet, DemandeUrgenteViewSet,
    CampagneViewSet, DonViewSet, ReponseAppelViewSet,
    StockSangViewSet, RendezVousViewSet, TransfertStockViewSet,
    NotificationViewSet, MessageViewSet
)

router = routers.DefaultRouter()
router.register('donneur', DonneurViewSet, basename='donneur')
router.register('hopital', HopitalViewSet, basename='hopital')
router.register('demande', DemandeUrgenteViewSet, basename='demande')
router.register('campagne', CampagneViewSet, basename='campagne')
router.register('don', DonViewSet, basename='don')
router.register('reponse', ReponseAppelViewSet, basename='reponse')
router.register('stock', StockSangViewSet, basename='stock')
router.register('rendezvous', RendezVousViewSet, basename='rendezvous')
router.register('transfert', TransfertStockViewSet, basename='transfert')
router.register('notification', NotificationViewSet, basename='notification')
router.register('message', MessageViewSet, basename='message')

urlpatterns += [
    path('api/', include(router.urls)),
]
