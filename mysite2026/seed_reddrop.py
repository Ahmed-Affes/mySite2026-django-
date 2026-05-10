import os
import django
import random
from datetime import timedelta, date
from django.utils import timezone

# Set up Django environment
import sys
project_path = r'c:\Users\ASUS PC\OneDrive\Documents\faculté\DSI23\django\venvDjango\mysite2026'
if project_path not in sys.path:
    sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite2026.settings')
django.setup()

from reddrop.models import Donneur, Hopital, DemandeUrgente, Campagne, Don, StockSang, RendezVous, Message, Notification, ReponseAppel
from django.contrib.auth.models import User

def seed_data():
    print("Starting seeding process...")
    
    hospitals = Hopital.objects.all()
    donors = Donneur.objects.all()
    
    if not hospitals or not donors:
        print("Error: Need at least one hospital and one donor in DB. Please register them manually first.")
        return

    # 1. Create more Urgent Requests
    print("Creating Urgent Requests...")
    blood_types = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    villes = ['Paris', 'Bordeaux', 'Lyon', 'Marseille']
    
    for _ in range(5):
        h = random.choice(hospitals)
        DemandeUrgente.objects.create(
            hopital=h,
            groupe_sanguin=random.choice(blood_types),
            quantite=random.randint(2, 12),
            delai=random.randint(1, 10),
            description="Besoin urgent suite à une intervention complexe.",
            ville=random.choice(villes),
            active=True
        )

    # 2. Create more Campaigns
    print("Creating Campaigns...")
    for _ in range(3):
        h = random.choice(hospitals)
        Campagne.objects.create(
            hopital=h,
            nom=f"Collecte {random.choice(['Printemps', 'Urgence Blood', 'Solidarité'])}",
            date=date.today() + timedelta(days=random.randint(5, 30)),
            lieu=f"Salle municipale {h.ville}",
            groupes_cibles="Tous groupes",
            capacite_totale=random.randint(20, 50),
            places_prises=random.randint(5, 15)
        )

    # 3. Create Donation History (Stats for Donors)
    print("Creating Donation History...")
    for d in donors:
        # Create 3-7 past donations for each donor
        for i in range(random.randint(3, 7)):
            past_date = date.today() - timedelta(days=random.randint(30, 800))
            h = random.choice(hospitals)
            don = Don.objects.create(
                donneur=d,
                hopital=h,
                date=past_date,
                groupe_sanguin=d.groupe_sanguin,
                quantite=1,
                lieu=h.nom
            )
            
            # Create corresponding Stock for hospital stats
            # Some are already used, some are in stock
            statut = random.choice(['OK', 'OK', 'OK', 'USED', 'EXP'])
            # Expiry date: 42 days for GR (Red Cells)
            expiry = don.date + timedelta(days=42)
            
            StockSang.objects.create(
                hopital=h,
                don=don,
                groupe_sanguin=don.groupe_sanguin,
                type_produit='GR',
                date_prelevement=don.date,
                date_peremption=expiry,
                statut=statut
            )

    # 4. Create Stock that is about to expire (for "Risque Péremption" stat)
    print("Creating Exiring Stock...")
    for h in hospitals:
        for _ in range(3):
            close_expiry = date.today() + timedelta(days=random.randint(1, 6))
            StockSang.objects.create(
                hopital=h,
                groupe_sanguin=random.choice(blood_types),
                type_produit='GR',
                date_prelevement=date.today() - timedelta(days=35),
                date_peremption=close_expiry,
                statut='OK'
            )

    # 5. Create RendezVous history
    print("Creating RDV History...")
    for _ in range(15):
        d = random.choice(donors)
        h = random.choice(hospitals)
        # Random status
        statut = random.choice(['P', 'H', 'A'])
        if statut == 'P':
            rdv_date = timezone.now() + timedelta(days=random.randint(1, 10))
        else:
            rdv_date = timezone.now() - timedelta(days=random.randint(1, 100))
            
        RendezVous.objects.create(
            donneur=d,
            hopital=h,
            date_heure=rdv_date,
            statut=statut
        )

    # 6. Create Messages
    print("Creating Messages...")
    for _ in range(10):
        u1 = random.choice(User.objects.all())
        u2 = random.choice(User.objects.exclude(id=u1.id))
        Message.objects.create(
            expediteur=u1,
            destinataire=u2,
            contenu=random.choice([
                "Bonjour, est-ce que je peux venir à 10h au lieu de 9h ?",
                "Merci beaucoup pour votre don !",
                "La campagne de demain est-elle maintenue ?",
                "Mon groupe est O-, puis-je donner aujourd'hui ?"
            ])
        )

    # 7. Create Notifications
    print("Creating Notifications...")
    for u in User.objects.all():
        for _ in range(random.randint(1, 4)):
            Notification.objects.create(
                user=u,
                titre="Information Système",
                message="Votre profil a été mis à jour avec succès.",
                lue=False
            )

    print("--- SUCCESS: Database seeded with dummy data! ---")

if __name__ == "__main__":
    seed_data()
