from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from magasin.models import Categorie, Fournisseur, Produit
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Creates test data for Magasin'

    def handle(self, *args, **options):
        self.stdout.write('🛒 Creating Magasin test data...')

        categories_data = [
            ('Electronique', 'Téléphones, ordinateurs, gadgets tech'),
            ('Vêtements', 'Mode pour homme, femme et enfants'),
            ('Maison', 'Meubles, décoration et jardin'),
            ('Sports', 'Équipements et vêtements sportifs'),
            ('Livres', 'Romans, учебники et magazines'),
            ('Beauté', 'Cosmétiques et soins personnels'),
            ('Jouets', 'Jeux et jouets pour enfants'),
            ('Automobile', 'Accessoires et pièces automobiles'),
        ]
        for name, desc in categories_data:
            if not Categorie.objects.filter(name=name).exists():
                Categorie.objects.create(name=name)
                self.stdout.write(f'  ✅ Category: {name}')

        suppliers_data = [
            ('TechWorld SARL', 'contact@techworld.tn', '71234567', 'Tunis, Avenue Habib Bourguiba'),
            ('Fashion Plus', 'info@fashionplus.tn', '98234567', 'Sfax, Rue de la Paix'),
            ('Home & Deco', 'contact@homedeco.tn', '73234567', 'Sousse, Zone Industrielle'),
            ('Sports Tunisia', 'ventes@sportstn.tn', '75234567', 'Ben Arous'),
            ('Beauté Orient', 'contact@beauteorient.tn', '99234567', 'Tunis, El Menzah'),
            ('Auto Parts TN', 'vente@autoparts.tn', '71234568', 'Ariena'),
        ]
        for nom, email, tel, adresse in suppliers_data:
            if not Fournisseur.objects.filter(nom=nom).exists():
                Fournisseur.objects.create(nom=nom, email=email, telephone=tel, adresse=adresse)
                self.stdout.write(f'  ✅ Supplier: {nom}')

        cat_elec = Categorie.objects.get(name='Electronique')
        cat_vet = Categorie.objects.get(name='Vêtements')
        cat_maison = Categorie.objects.get(name='Maison')
        cat_sports = Categorie.objects.get(name='Sports')
        cat_beaute = Categorie.objects.get(name='Beauté')
        cat_jouets = Categorie.objects.get(name='Jouets')

        suppliers = list(Fournisseur.objects.all())

        products_data = [
            ('iPhone 15 Pro Max', 'iPhone 15 Pro Max 256GB - Titanium', 1499.00, cat_elec, 'https://images.unsplash.com/photo-1592750475338-74b7b21085a5?w=400'),
            ('MacBook Pro 16"', 'MacBook Pro M3 Max 16" - Space Black', 2499.00, cat_elec, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400'),
            ('Samsung Galaxy S24 Ultra', 'Samsung Galaxy S24 Ultra 512GB', 1199.00, cat_elec, 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400'),
            ('iPad Pro 12.9"', 'iPad Pro 12.9" M2 256GB WiFi', 1099.00, cat_elec, 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400'),
            ('AirPods Max', 'AirPods Max Silver - Casque Premium', 549.00, cat_elec, 'https://images.unsplash.com/photo-1625245488600-f03fef636a3c?w=400'),
            ('Apple Watch Ultra 2', 'Apple Watch Ultra 2 49mm', 799.00, cat_elec, 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400'),
            ('Sony WH-1000XM5', 'Sony WH-1000XM5 - Casque Noise Cancelling', 349.00, cat_elec, 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400'),
            ('Nintendo Switch OLED', 'Nintendo Switch OLED Model', 349.00, cat_elec, 'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400'),
            
            ('Chemise Coton Premium', 'Chemise homme 100% coton slim fit', 49.00, cat_vet, 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400'),
            ('Jean Skinny Fit', 'Jean homme skinny stretch noir', 65.00, cat_vet, 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400'),
            ('Robe Summer Florale', 'Robe femme été fleuri', 79.00, cat_vet, 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400'),
            ('Sneakers Sport', 'Sneakers running homme', 89.00, cat_vet, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),
            ('Veste en Cuir', 'Veste cuir femme motif', 199.00, cat_vet, 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400'),
            ('Polo Classic', 'Polo homme cotton piqué', 35.00, cat_vet, 'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=400'),
            ('Pantalon Chino', 'Pantalon chino homme beige', 55.00, cat_vet, 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400'),
            ('Sac à Main Cuir', 'Sac à main femme cuir véritable', 129.00, cat_vet, 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400'),
            
            ('Canapé L Shape', 'Canapé en U gris foncé', 1299.00, cat_maison, 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400'),
            ('Table à Manger Bois', 'Table à manger 6 personnes chêne', 599.00, cat_maison, 'https://images.unsplash.com/photo-1617806118233-18e1de247200?w=400'),
            ('Lampe Salon Moderne', 'Lampe à poser salon design', 79.00, cat_maison, 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400'),
            ('Rideaux Occultants', 'Rideaux occultants 200x260cm', 45.00, cat_maison, 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=400'),
            ('Ensemble Literie', 'Ensemble drap + housse 200TC', 89.00, cat_maison, 'https://images.unsplash.com/photo-1522771739844-6a9f6d5f9c8f?w=400'),
            ('Fauteuil Relax', 'Fauteuil relax inclinable', 349.00, cat_maison, 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400'),
            
            ('Tapis de Yoga', 'Tapis yoga 6mm anti-dérapant', 25.00, cat_sports, 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400'),
            ('Haltères Set 20kg', 'Set haltères + barre 20kg', 89.00, cat_sports, 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400'),
            ('Vélos d\'Appartement', 'Vélo elliptique pliant', 399.00, cat_sports, 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400'),
            ('Ballon Football', 'Ballon football match pro', 35.00, cat_sports, 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=400'),
            ('Raquette Tennis', 'Raquette tennis carbone', 79.00, cat_sports, 'https://images.unsplash.com/photo-1617083934551-ac1f1b6a50e8?w=400'),
            ('Sac de Sport', 'Sac sport 40L waterproof', 45.00, cat_sports, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'),
            
            ('Parfum Femme', 'Parfum femme 100ml floral', 89.00, cat_beaute, 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=400'),
            ('Parfum Homme', 'Parfum homme 100ml boisé', 79.00, cat_beaute, 'https://images.unsplash.com/photo-1594035910387-fea47794261f?w=400'),
            ('Crème Hydratante', 'Crème hydratante visage 50ml', 35.00, cat_beaute, 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400'),
            ('Kit Maquillage', 'Kit maquillage professionnelle', 69.00, cat_beaute, 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400'),
            ('Sèche Cheveux Pro', 'Sèche cheveux 2000W ionique', 79.00, cat_beaute, 'https://images.unsplash.com/photo-1583384256473-0a7455aa9f92?w=400'),
            
            ('Lego City Pack', 'Lego City Extreme (500 pcs)', 45.00, cat_jouets, 'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400'),
            ('Poupée Barbie', 'Poupée fashion girlaccessories', 29.00, cat_jouets, 'https://images.unsplash.com/photo-1558679908-541bcf124a68?w=400'),
            ('Voiture Télécommandée', 'Voiture RC 1:18 vitesse 30km/h', 79.00, cat_jouets, 'https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=400'),
            ('Puzzle 1000 Pièces', 'Puzzle paysage naturel', 19.00, cat_jouets, 'https://images.unsplash.com/photo-1494059980473-813e73ee784b?w=400'),
            ('Ballon de Basket', 'Ballon basketball Wilson', 25.00, cat_jouets, 'https://images.unsplash.com/photo-1519861531473-92002639313cc?w=400'),
        ]

        for libelle, description, prix, categorie, image_url in products_data:
            if not Produit.objects.filter(libelle=libelle).exists():
                Produit.objects.create(
                    libelle=libelle,
                    description=description,
                    prix=prix,
                    categorie=categorie,
                    fournisseur=random.choice(suppliers),
                    stock=random.randint(10, 100),
                    type=libelle,
                    is_active=True,
                    image=image_url
                )
                self.stdout.write(f'  ✅ Product: {libelle}')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Created {Produit.objects.count()} products!'))