import os
import django
import random
from django.utils import timezone
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite2026.settings')
django.setup()

from magasin.models import (
    Categorie, Fournisseur, Produit, Commande, CommandeLigne, 
    BonDeCommande, BonDeCommandeLigne, ProduitFournisseur, User
)

def seed():
    print("--- Wiping old data... ---")
    Notification.objects.all().delete()
    Commande.objects.all().delete()
    BonDeCommande.objects.all().delete()
    Produit.objects.all().delete()
    Fournisseur.objects.all().delete()
    Categorie.objects.all().delete()

    print("--- Creating Categories... ---")
    cats = [
        Categorie.objects.create(name="Electronique"),
        Categorie.objects.create(name="Mobilier"),
        Categorie.objects.create(name="Vetements"),
        Categorie.objects.create(name="Outillage"),
        Categorie.objects.create(name="Alimentation"),
    ]

    print("--- Creating Suppliers... ---")
    # Define specialties for suppliers
    suppliers = {
        "tech": Fournisseur.objects.create(nom="TechWorld Solutions", email="sales@techworld.tn", telephone="+216 71 111 222", adresse="Z.I. Ariana, Tunis"),
        "furniture": Fournisseur.objects.create(nom="Global Furniture Co.", email="contact@globalfurn.com", telephone="+216 72 333 444", adresse="Route de Sousse, Hammamet"),
        "clothing": Fournisseur.objects.create(nom="Elite Garments", email="b2b@elitegarments.tn", telephone="+216 73 555 666", adresse="Zone Industrielle, Monastir"),
        "tools": Fournisseur.objects.create(nom="Master Tools SARL", email="info@mastertools.tn", telephone="+216 74 777 888", adresse="Sfax El Jadida"),
        "food": Fournisseur.objects.create(nom="BioFood Distrib", email="order@biofood.tn", telephone="+216 70 999 000", adresse="Marche de Gros, Bir El Kassaa"),
    }
    
    # Generic supplier that can do multiple things
    general = Fournisseur.objects.create(nom="OmniTrade Logistics", email="ops@omnitrade.tn", telephone="+216 75 000 111", adresse="Port de Rades")

    print("--- Creating Products & Sources... ---")
    # Format: (Name, Category, Retail Price, Buy Price, Specialty Key)
    products_data = [
        # Electronics
        ("MacBook Air M2", cats[0], 3500.00, 2800.00, "tech"),
        ("iPhone 15 Pro", cats[0], 4200.00, 3200.00, "tech"),
        ("AirPods Pro 2", cats[0], 850.00, 600.00, "tech"),
        ("Moniteur 4K 27", cats[0], 1200.00, 850.00, "tech"),
        # Furniture
        ("Bureau Ergonomique", cats[1], 850.00, 500.00, "furniture"),
        ("Chaise de Bureau", cats[1], 450.00, 250.00, "furniture"),
        ("Lampe LED Design", cats[1], 120.00, 60.00, "furniture"),
        # Tools
        ("Perceuse Sans Fil", cats[3], 320.00, 180.00, "tools"),
        ("Coffret de Douilles", cats[3], 150.00, 80.00, "tools"),
        ("Escabeau 5 Marches", cats[3], 210.00, 120.00, "tools"),
        # Clothing
        ("Veste Impermeable", cats[2], 180.00, 90.00, "clothing"),
        ("T-shirt Coton Bio", cats[2], 45.00, 20.00, "clothing"),
        # Food
        ("Pack Cafe 1kg", cats[4], 35.00, 22.00, "food"),
        ("Huile d'Olive 5L", cats[4], 120.00, 85.00, "food"),
    ]

    import urllib.request, shutil, os

    # Specific picsum IDs that visually match each product
    PRODUCT_PHOTOS = {
        'macbook':   '119',   # laptop on desk
        'iphone':    '250',   # smartphone
        'airpods':   '350',   # tech/earbuds feel
        'moniteur':  '375',   # screen/monitor
        'bureau':    '380',   # office/desk
        'chaise':    '634',   # chair
        'lampe':     '435',   # lamp/light
        'perceuse':  '239',   # tools
        'coffret':   '167',   # toolbox
        'escabeau':  '292',   # stepladder
        'veste':     '338',   # jacket/clothing
        't-shirt':   '447',   # clothing
        'cafe':      '431',   # coffee
        'huile':     '292',   # food/olive
    }

    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'produits')
    os.makedirs(media_dir, exist_ok=True)

    created_products = []
    for name, cat, price, p_buy, specialty in products_data:
        # Determine type code
        p_type = 'au'
        if specialty == 'tech': p_type = 'el'
        elif specialty == 'furniture': p_type = 'mo'
        elif specialty == 'clothing': p_type = 've'
        elif specialty == 'tools': p_type = 'ou'
        elif specialty == 'food': p_type = 'al'

        p = Produit.objects.create(
            libelle=name,
            categorie=cat,
            description=f"Description professionnelle pour {name}. Qualite superieure garantie.",
            prix=price,
            stock=random.randint(2, 50),
            stock_minimum=random.randint(5, 15),
            type=p_type,
            image='' # Fallback to model's image_url property
        )
        created_products.append(p)

        # LOGIC: Link to the specialist supplier + the general supplier as backup
        specialist = suppliers[specialty]
        ProduitFournisseur.objects.create(
            produit=p, fournisseur=specialist,
            prix_achat=p_buy,
            delai_livraison_jours=random.randint(1, 2),
            is_preferred=True
        )
        ProduitFournisseur.objects.create(
            produit=p, fournisseur=general,
            prix_achat=p_buy * 1.1,
            delai_livraison_jours=random.randint(3, 5),
            is_preferred=False
        )

    print("--- Creating Sample Orders... ---")
    user = User.objects.filter(is_superuser=False).first() or User.objects.first()
    
    statuses = ['en_attente', 'confirmee', 'expediee', 'livree']
    for i in range(10):
        c = Commande.objects.create(
            client=user,
            dateCde=timezone.now().date() - timedelta(days=random.randint(0, 30)),
            status=random.choice(statuses)
        )
        total = 0
        for _ in range(random.randint(1, 4)):
            p = random.choice(created_products)
            qty = random.randint(1, 3)
            CommandeLigne.objects.create(commande=c, produit=p, quantite=qty, prix_unitaire=p.prix)
            total += p.prix * qty
        c.totalCde = total
        c.save()

    print("--- Creating Sample BDCs... ---")
    all_suppliers = list(suppliers.values()) + [general]
    bdc_statuses = ['brouillon', 'envoye', 'accepte', 'recu']
    for i in range(5):
        s = random.choice(all_suppliers)
        bdc = BonDeCommande.objects.create(
            fournisseur=s,
            cree_par=User.objects.filter(is_staff=True).first(),
            statut=random.choice(bdc_statuses),
            notes="Commande de reapprovisionnement mensuelle."
        )
        # Only add products that this supplier actually supplies
        available_prods = Produit.objects.filter(sources__fournisseur=s)
        if available_prods.exists():
            for p in random.sample(list(available_prods), min(len(available_prods), 3)):
                source = ProduitFournisseur.objects.get(produit=p, fournisseur=s)
                BonDeCommandeLigne.objects.create(bon=bdc, produit=p, quantite=random.randint(10, 30), prix_achat=source.prix_achat)

    print("--- Database Seeded Successfully with Logical Mapping! ---")



if __name__ == "__main__":
    seed()
