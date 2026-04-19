from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='blood_home'),
    path('connexion/', views.login_view, name='blood_login'),
    path('deconnexion/', views.logout_view, name='blood_logout'),
    path('inscription/donneur/', views.register_donneur, name='register_donneur'),
    path('inscription/hopital/', views.register_hopital, name='register_hopital'),
    path('dashboard/', views.dashboard, name='blood_dashboard'),
    path('demandes/', views.urgent_requests, name='blood_demandes'),
    path('demandes/nouveau/', views.publish_request, name='publish_request'),
    path('demandes/<int:pk>/modifier/', views.edit_request, name='edit_request'),
    path('demandes/<int:pk>/supprimer/', views.delete_request, name='delete_request'),
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
    path('rendezvous/<int:pk>/statut/<str:status>/', views.update_rendezvous_status, name='update_rdv_status'),
]
