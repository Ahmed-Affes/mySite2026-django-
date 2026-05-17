from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Donneur, Hopital, DemandeUrgente, Campagne, Don,
    ReponseAppel, StockSang, RendezVous, TransfertStock,
    Notification, Message
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class DonneurSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Donneur
        fields = ['id', 'user', 'user_details', 'groupe_sanguin', 'sexe', 'date_naissance', 'ville', 'actif', 'dernier_don']


class HopitalSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Hopital
        fields = ['id', 'user', 'user_details', 'nom', 'adresse', 'ville', 'numero_agrement', 'valide']


class DemandeUrgenteSerializer(serializers.ModelSerializer):
    hopital_details = HopitalSerializer(source='hopital', read_only=True)
    
    class Meta:
        model = DemandeUrgente
        fields = ['id', 'hopital', 'hopital_details', 'groupe_sanguin', 'quantite', 'delai', 'description', 'ville', 'active', 'cree_le']


class CampagneSerializer(serializers.ModelSerializer):
    hopital_details = HopitalSerializer(source='hopital', read_only=True)
    
    class Meta:
        model = Campagne
        fields = ['id', 'hopital', 'hopital_details', 'nom', 'date', 'lieu', 'groupes_cibles', 'capacite_totale', 'places_prises', 'valide']


class DonSerializer(serializers.ModelSerializer):
    donneur_details = DonneurSerializer(source='donneur', read_only=True)
    hopital_details = HopitalSerializer(source='hopital', read_only=True)

    class Meta:
        model = Don
        fields = ['id', 'donneur', 'donneur_details', 'hopital', 'hopital_details', 'date', 'groupe_sanguin', 'quantite', 'lieu']


class ReponseAppelSerializer(serializers.ModelSerializer):
    demande_details = DemandeUrgenteSerializer(source='demande', read_only=True)
    donneur_details = DonneurSerializer(source='donneur', read_only=True)

    class Meta:
        model = ReponseAppel
        fields = ['id', 'demande', 'demande_details', 'donneur', 'donneur_details', 'date_reponse', 'statut', 'commentaire']


class StockSangSerializer(serializers.ModelSerializer):
    hopital_details = HopitalSerializer(source='hopital', read_only=True)
    don_details = DonSerializer(source='don', read_only=True)

    class Meta:
        model = StockSang
        fields = ['id', 'hopital', 'hopital_details', 'don', 'don_details', 'groupe_sanguin', 'type_produit', 'date_prelevement', 'date_peremption', 'statut']


class RendezVousSerializer(serializers.ModelSerializer):
    donneur_details = DonneurSerializer(source='donneur', read_only=True)
    hopital_details = HopitalSerializer(source='hopital', read_only=True)
    campagne_details = CampagneSerializer(source='campagne', read_only=True)

    class Meta:
        model = RendezVous
        fields = ['id', 'donneur', 'donneur_details', 'hopital', 'hopital_details', 'campagne', 'campagne_details', 'date_heure', 'statut']


class TransfertStockSerializer(serializers.ModelSerializer):
    hopital_demandeur_details = HopitalSerializer(source='hopital_demandeur', read_only=True)
    hopital_fournisseur_details = HopitalSerializer(source='hopital_fournisseur', read_only=True)

    class Meta:
        model = TransfertStock
        fields = ['id', 'hopital_demandeur', 'hopital_demandeur_details', 'hopital_fournisseur', 'hopital_fournisseur_details', 'groupe_sanguin', 'quantite', 'statut', 'date_demande']


class NotificationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_details', 'titre', 'message', 'date_creation', 'lue', 'lien']


class MessageSerializer(serializers.ModelSerializer):
    expediteur_details = UserSerializer(source='expediteur', read_only=True)
    destinataire_details = UserSerializer(source='destinataire', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'expediteur', 'expediteur_details', 'destinataire', 'destinataire_details', 'contenu', 'date_envoi', 'lue']
