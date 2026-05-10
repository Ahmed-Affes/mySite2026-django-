import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite2026.settings')
django.setup()

from magasin.models import Categorie, Fournisseur, Produit

# Create categories
categories_data = [
    ('Al', 'Alimentaire'),
    ('Mb', 'Meuble'),
    ('Sn', 'Sanitaire'),
    ('Vs', 'Vaisselle'),
    ('Vt', 'Vêtement'),
    ('Jx', 'Jouets'),
    ('Lg', 'Linge de Maison'),
    ('Bj', 'Bijoux'),
    ('Dc', 'Décor')
]

categories = {}
for code, name in categories_data:
    cat, created = Categorie.objects.get_or_create(name=code)
    categories[code] = cat

# Create suppliers
suppliers_data = [
    ('Fournisseur A', 'Adresse A', 'a@example.com', '12345678'),
    ('Fournisseur B', 'Adresse B', 'b@example.com', '87654321'),
    ('Fournisseur C', 'Adresse C', 'c@example.com', '11223344'),
]

suppliers = []
for nom, adresse, email, tel in suppliers_data:
    sup, created = Fournisseur.objects.get_or_create(
        nom=nom,
        defaults={'adresse': adresse, 'email': email, 'telephone': tel}
    )
    suppliers.append(sup)

# Create products
products_data = [
    ('Pain frais', 'Du pain tout chaud', 2.5, 'fr', 'Al', suppliers[0], 50),
    ('Table en bois', 'Belle table pour salle à manger', 150.0, 'em', 'Mb', suppliers[1], 10),
    ('Savon liquide', 'Savon pour les mains', 5.0, 'em', 'Sn', suppliers[2], 100),
    ('Assiette blanche', 'Assiette en porcelaine', 8.0, 'em', 'Vs', suppliers[0], 30),
    ('T-shirt rouge', 'T-shirt en coton', 15.0, 'em', 'Vt', suppliers[1], 20),
    ('Jouet voiture', 'Voiture téléguidée', 25.0, 'em', 'Jx', suppliers[2], 15),
    ('Drap de lit', 'Draps pour lit double', 30.0, 'em', 'Lg', suppliers[0], 25),
    ('Collier argent', 'Collier en argent massif', 50.0, 'em', 'Bj', suppliers[1], 5),
    ('Vase décoratif', 'Vase en verre', 20.0, 'em', 'Dc', suppliers[2], 12),
]

for libelle, desc, prix, typ, cat_code, forn, stk in products_data:
    prod, created = Produit.objects.get_or_create(
        libelle=libelle,
        defaults={
            'description': desc,
            'prix': prix,
            'type': typ,
            'categorie': categories[cat_code],
            'fornisseur': forn,
            'img': 'produits/default.jpg',
            'stock': stk
        }
    )

print("Sample data added successfully!")