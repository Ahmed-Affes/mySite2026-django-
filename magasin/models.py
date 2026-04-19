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