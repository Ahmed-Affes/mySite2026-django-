"""
magasin/models.py  —  Complete models matching the actual db.sqlite3 schema
"""

from django.db import models
from django.contrib.auth.models import User


class Categorie(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name        = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering            = ['name']

    def __str__(self):
        return self.name


class Fournisseur(models.Model):
    nom       = models.CharField(max_length=100)
    adresse   = models.TextField()
    email     = models.EmailField()
    telephone = models.CharField(max_length=8)

    class Meta:
        verbose_name        = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering            = ['nom']

    def __str__(self):
        return self.nom


class Produit(models.Model):
    TYPE_CHOICES = [
        ('em', 'Électroménager'),
        ('cs', 'Consommable'),
        ('fr', 'Fruits & Légumes'),
        ('ve', 'Vêtement'),
        ('bi', 'Bijoux'),
        ('au', 'Autre'),
    ]

    type        = models.CharField(max_length=2, choices=TYPE_CHOICES)
    libelle     = models.CharField(max_length=100)
    description = models.TextField()
    prix        = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True, verbose_name="Actif")
    categorie   = models.ForeignKey(Categorie,  on_delete=models.PROTECT)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT)
    image       = models.ImageField(upload_to='produits/', blank=True, null=True)

    class Meta:
        verbose_name        = 'Produit'
        verbose_name_plural = 'Produits'
        ordering            = ['libelle']

    def __str__(self):
        return self.libelle

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            try:
                # Check if file exists to avoid broken links
                if self.image.storage.exists(self.image.name):
                    return self.image.url
            except Exception:
                pass
        
        # 1. Premium Mapping with stable Unsplash IDs for common products
        # These are high-quality, fixed photos that will never change
        premium_photos = {
            'airpods': 'photo-1588423771073-b8903fbb85b5',  # Generic AirPods
            'watch': 'photo-1434494878577-86c23bcb06b9',    # Apple Watch
            'iphone': 'photo-1510557880182-3d4d3cba35a5',
            'phone': 'photo-1511707171634-5f897ff02aa9',
            'ordinateur': 'photo-1496181133206-80ce9b88a853',
            'laptop': 'photo-1496181133206-80ce9b88a853',
            'pain': 'photo-1509440159596-0249088772ff',
            'table': 'photo-1530018607912-eff2df114f11',
            'savon': 'photo-1600857062241-75e54720121a',
            'ballon': 'photo-1574629810360-7efbbe195018',
            'football': 'photo-1574629810360-7efbbe195018',
            'basket': 'photo-1519861531473-9200262188bf',
            'canapé': 'photo-1493663284031-b7e3aefcae8e',
            'sofa': 'photo-1493663284031-b7e3aefcae8e',
            'vase': 'photo-1581783898377-1c85bf937427',
            't-shirt': 'photo-1521572267360-ee0c2909d518',
            'chaussures': 'photo-1542291026-7eec264c27ff',
            'lunettes': 'photo-1572635196237-14b3f281503f',
            'parfum': 'photo-1541643600914-78b084683601',
            'bijoux': 'photo-1515562141207-7a88fb0ce33e',
            'collier': 'photo-1515562141207-7a88fb0ce33e',
        }
        
        query = self.libelle.lower()
        for key, photo_id in premium_photos.items():
            if key in query:
                return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=800&q=80"

        # 2. Category Fallback with codes
        cat_photos = {
            'al': 'photo-1506617564534-20a2f500030c', # Food
            'mb': 'photo-1524758631624-e2822e304c36', # Furniture
            'sn': 'photo-1584622650111-993a426fbf0a', # Hygiene
            'vs': 'photo-1516715662039-c52981cca40b', # Dishware
            'vt': 'photo-1489987707025-afc232f7ea0f', # Clothing
            'jx': 'photo-1539627831859-a911cf04b0c7', # Toys
            'lg': 'photo-1522771739844-6a9f6d5f14af', # Bedroom
            'bj': 'photo-1573408302382-9014b024400e', # Jewelry
            'dc': 'photo-1534349762230-e0cadf78f5db', # Decor
        }
        
        if self.categorie:
            code = self.categorie.name.lower()
            if code in cat_photos:
                return f"https://images.unsplash.com/{cat_photos[code]}?auto=format&fit=crop&w=800&q=80"
        
        # 3. Final Fallback (Fixed per product ID)
        return f"https://picsum.photos/seed/{self.id}/800/600"


class Commande(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee',  'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('expediee',  'Expédiée'),
        ('livree',    'Livrée'),
        ('annulee',   'Annulée'),
    ]

    client    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commandes', null=True, blank=True)
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    totalCde  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dateCde   = models.DateField()
    produits  = models.ManyToManyField(Produit, blank=True)
    
    adresse_livraison = models.CharField(max_length=255, default="", blank=True)
    telephone_contact = models.CharField(max_length=20, default="", blank=True)
    email_contact     = models.EmailField(default="", blank=True)

    class Meta:
        verbose_name        = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering            = ['-dateCde']

    def __str__(self):
        return f'Commande #{self.id} — {self.dateCde}'


class Wishlist(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'produit')
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.username} - {self.produit.libelle}'


class Review(models.Model):
    produit   = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='reviews')
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating    = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment   = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('produit', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.produit.libelle} - {self.rating}★'