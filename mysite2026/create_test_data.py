import os
import django
from datetime import timedelta
from django.utils import timezone
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite2026.settings")
django.setup()

from django.contrib.auth.models import User
from reddrop.models import Hopital, Donneur, StockSang, RendezVous, DemandeUrgente, Campagne, TransfertStock, Don, Message

def create_bulk():
    print("Clearing old data...")
    Donneur.objects.all().delete()
    Hopital.objects.all().delete()
    StockSang.objects.all().delete()
    DemandeUrgente.objects.all().delete()
    Campagne.objects.all().delete()
    RendezVous.objects.all().delete()
    Message.objects.all().delete()
    # It's fine to leave old Users orphaned for a mock environment.
    
    cities = ['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille']
    blood_types = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']

    print("Creating Hospitals...")
    hospitals_data = [
        ("hosp_paris", "Hôpital Central de Paris", "12 Ave de France", "Paris"),
        ("hosp_lyon", "CHU de Lyon", "8 Rue Edouard Herriot", "Lyon"),
        ("hosp_marseille", "Hôpital de la Timone", "264 Rue Saint-Pierre", "Marseille"),
        ("hosp_bordeaux", "CHU Pellegrin", "Place Amélie Raba Léon", "Bordeaux")
    ]
    
    hospitals = []
    for username, nom, adresse, ville in hospitals_data:
        h_user, _ = User.objects.get_or_create(username=username, defaults={'email': f"{username}@reddrop.com"})
        h_user.set_password("Reddrop123!")
        h_user.save()
        h, _ = Hopital.objects.get_or_create(user=h_user, defaults={'nom': nom, 'adresse': adresse, 'ville': ville, 'numero_agrement': f"AGR-{random.randint(1000, 9999)}", 'valide': True})
        hospitals.append(h)
        print(f" - Created {nom}")

    print("Creating Donors...")
    donors = []
    for i in range(1, 15):
        d_user, _ = User.objects.get_or_create(username=f"donneur_{i}", defaults={'email': f"donneur{i}@reddrop.com"})
        d_user.set_password("Reddrop123!")
        d_user.save()
        bg = random.choice(blood_types)
        sexe = random.choice(['M', 'F'])
        d, _ = Donneur.objects.get_or_create(
            user=d_user, defaults={'groupe_sanguin': bg, 'sexe': sexe,
            'date_naissance': timezone.now().date() - timedelta(days=random.randint(7000, 15000)),
            'ville': random.choice(cities)}
        )
        donors.append(d)
    print(f" - Created 14 Donors with various blood types")

    print("Creating 20+ Bags of Stock...")
    for _ in range(25):
        StockSang.objects.create(
            hopital=random.choice(hospitals),
            type_produit=random.choice(['GR', 'PL', 'PS']),
            groupe_sanguin=random.choice(blood_types),
            date_prelevement=timezone.now().date() - timedelta(days=random.randint(0, 10)),
            statut=random.choice(['OK', 'OK', 'OK', 'TEST', 'TEST'])
        )
        
    print("Creating 12 Urgent Demands...")
    reasons = [
        "Urgence bloc opératoire suite accident de la route.",
        "Patient hémophile en besoin immédiat.",
        "Transfusion nécessaire pour chirurgie cardiaque.",
        "Complication lors d'un accouchement, besoin urgent.",
        "Besoin de plaquettes pour patient sous chimiothérapie.",
        "Accident industriel grave.",
        "Patient atteint de leucémie en crise.",
        "Chirurgie orthopédique majeure."
    ]
    for _ in range(12):
        DemandeUrgente.objects.create(
            hopital=random.choice(hospitals),
            groupe_sanguin=random.choice(['O-', 'A-', 'B-', 'AB-', 'A+', 'O+']),
            quantite=random.randint(1, 10),
            delai=random.randint(1, 5),
            description=random.choice(reasons),
            ville=random.choice(cities),
            active=True
        )

    print("Creating 5 Campagnes...")
    for i in range(1, 6):
        campagne_names = ['Solidaire', 'Printaniere', 'dUrgence', 'Mensuelle', 'Estivale']
        Campagne.objects.create(
            hopital=random.choice(hospitals),
            nom=f"Grande Collecte {campagne_names[i-1]}",
            date=timezone.now().date() + timedelta(days=random.randint(2, 30)),
            lieu=random.choice(["Université", "Mairie", "Place Centrale", "Salle des Fêtes"]),
            capacite_totale=random.choice([50, 100, 150, 200]),
            places_prises=random.randint(0, 40)
        )

    print("Creating 15 Rendez-Vous...")
    for _ in range(15):
        RendezVous.objects.create(
            donneur=random.choice(donors),
            hopital=random.choice(hospitals),
            date_heure=timezone.now() + timedelta(days=random.randint(1, 10), hours=random.randint(8, 16)),
            statut=random.choice(['P', 'P', 'P', 'P', 'H', 'A'])
        )

    print("Creating Donation History (12 random donations)...")
    for i, d in enumerate(donors):
        if i == 0:
            # Force first donor to be NOT eligible (donated yesterday)
            d_date = timezone.now().date() - timedelta(days=1)
        else:
            # last donation at least 4 months ago
            d_date = timezone.now().date() - timedelta(days=random.randint(120, 500))
        
        Don.objects.create(
            donneur=d,
            hopital=random.choice(hospitals),
            date=d_date,
            groupe_sanguin=d.groupe_sanguin,
            quantite=1,
            lieu=random.choice(cities)
        )
        # Update donor's last donation date if it's more recent
        if not d.dernier_don or d_date > d.dernier_don:
            d.dernier_don = d_date
            d.save()

    print("Creating Test Messages...")
    hp_user = User.objects.get(username="hosp_paris")
    d1_user = User.objects.get(username="donneur_1")
    Message.objects.create(
        expediteur=d1_user, destinataire=hp_user,
        contenu="Bonjour, je suis disponible pour l'urgence O- demain matin."
    )
    Message.objects.create(
        expediteur=hp_user, destinataire=d1_user,
        contenu="C'est parfait. Nous vous attendons à partir de 8h00. Merci !"
    )

    print("====================================")
    print("MOCK DATA SUCCESSFULLY SEEDED!")
    print("You now have:")
    print(" - 4 Hospitals (ex: hosp_paris / Reddrop123!)")
    print(" - 14 Donors (ex: donneur_1 / Reddrop123!)")
    print(" - Dozens of Active Urgent Requests, Stocks, Campaigns & Appointments!")
    print("====================================")

if __name__ == "__main__":
    create_bulk()
