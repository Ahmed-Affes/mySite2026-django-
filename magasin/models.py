"""
magasin/models.py  —  Enterprise-grade models for the magasin app
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum


# ──────────────────────────────────────────────────────────────
# Catégorie
# ──────────────────────────────────────────────────────────────
class Categorie(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name        = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering            = ['name']

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────────────────────
# Fournisseur
# ──────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────
# Produit
# ──────────────────────────────────────────────────────────────
class Produit(models.Model):
    TYPE_CHOICES = [
        ('em', 'Électroménager'),
        ('el', 'Électronique'),
        ('mo', 'Mobilier'),
        ('ve', 'Vêtement'),
        ('ou', 'Outillage'),
        ('al', 'Alimentation'),
        ('au', 'Autre'),
    ]

    type          = models.CharField(max_length=2, choices=TYPE_CHOICES)
    libelle       = models.CharField(max_length=100)
    description   = models.TextField()
    prix          = models.DecimalField(max_digits=10, decimal_places=2)
    prix_achat    = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock         = models.PositiveIntegerField(default=0)
    stock_minimum = models.PositiveIntegerField(default=5, verbose_name="Stock minimum (alerte)")
    is_active     = models.BooleanField(default=True, verbose_name="Actif")
    categorie     = models.ForeignKey(Categorie,   on_delete=models.PROTECT)
    image         = models.ImageField(upload_to='produits/', blank=True, null=True)
    
    # We remove the single supplier FK and use a ManyToMany through a mapping table
    # to support professional multi-sourcing with different prices.
    fournisseurs  = models.ManyToManyField(Fournisseur, through='ProduitFournisseur', related_name='produits_proposes')

    class Meta:
        verbose_name        = 'Produit'
        verbose_name_plural = 'Produits'
        ordering            = ['libelle']

    def __str__(self):
        return self.libelle

    @property
    def is_low_stock(self):
        return self.stock <= self.stock_minimum

    @property
    def meilleur_fournisseur(self):
        """Returns the supplier with the lowest purchase price for this product."""
        best = self.sources.order_by('prix_achat').first()
        return best.fournisseur if best else None

    @property
    def prix_achat_moyen(self):
        avg = self.sources.aggregate(models.Avg('prix_achat'))['prix_achat__avg']
        return avg or self.prix_achat

    @property
    def image_url(self):
        # Use local uploaded image if available
        if self.image and self.image.name:
            try:
                return self.image.url
            except Exception:
                pass

        # Direct Pexels CDN URLs — verified, free, permanently hosted
        PEXELS_PHOTOS = {
            'macbook':  '2506947',   # MacBook on desk
            'iphone':   '788946',    # iPhone flat lay
            'airpods':  '3780681',   # white wireless earbuds
            'moniteur': '1714208',   # computer monitor
            'bureau':   '1957477',   # wooden office desk
            'chaise':   '1957478',   # office chair
            'lampe':    '1112598',   # modern desk lamp
            'perceuse': '162553',    # power drill
            'coffret':  '1249611',   # wrench and tools
            'escabeau': '209416',    # step ladder
            'veste':    '1040173',   # jacket clothing
            't-shirt':  '991509',    # white t-shirt
            'cafe':     '894695',    # coffee beans
            'huile':    '2294477',   # olive oil bottle
        }

        query = self.libelle.lower()
        photo_id = None
        for keyword, pid in PEXELS_PHOTOS.items():
            if keyword in query:
                photo_id = pid
                break

        if not photo_id and self.categorie:
            CAT_FALLBACKS = {
                'electronique': '356056',
                'mobilier':     '1350789',
                'vetements':    '996329',
                'outillage':    '175039',
                'alimentation': '1640777',
            }
            cat = self.categorie.name.lower()
            for key, pid in CAT_FALLBACKS.items():
                if key in cat:
                    photo_id = pid
                    break

        if photo_id:
            return (
                f"https://images.pexels.com/photos/{photo_id}/"
                f"pexels-photo-{photo_id}.jpeg"
                f"?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"
            )

        return f"https://picsum.photos/seed/{self.id}/800/600"


class ProduitFournisseur(models.Model):
    """Intermediary model to link products to multiple suppliers with specific pricing."""
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='sources')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='offres')
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    delai_livraison_jours = models.PositiveIntegerField(default=3)
    is_preferred = models.BooleanField(default=False)

    class Meta:
        unique_together = ('produit', 'fournisseur')
        verbose_name = "Source d'approvisionnement"

    def __str__(self):
        return f"{self.fournisseur.nom} -> {self.produit.libelle} ({self.prix_achat} DT)"




# ──────────────────────────────────────────────────────────────
# Commande  (Order header — one row per order)
# ──────────────────────────────────────────────────────────────
class Commande(models.Model):
    STATUS_CHOICES = [
        ('en_attente',    'En attente'),
        ('confirmee',     'Confirmée'),
        ('en_preparation','En préparation'),
        ('expediee',      'Expédiée'),
        ('livree',        'Livrée'),
        ('annulee',       'Annulée'),
    ]

    client    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commandes', null=True, blank=True)
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    totalCde  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dateCde   = models.DateField()

    # Legacy M2M kept so old data is not broken — new orders use CommandeLigne
    produits  = models.ManyToManyField(Produit, blank=True)

    adresse_livraison = models.CharField(max_length=255, default='', blank=True)
    telephone_contact = models.CharField(max_length=20,  default='', blank=True)
    email_contact     = models.EmailField(default='',    blank=True)

    # Admin workflow fields
    note_admin        = models.TextField(blank=True, verbose_name="Note interne admin")
    raison_annulation = models.TextField(blank=True, verbose_name="Raison d'annulation")
    date_confirmation = models.DateTimeField(null=True, blank=True)
    date_expedition   = models.DateTimeField(null=True, blank=True)
    date_livraison    = models.DateTimeField(null=True, blank=True)
    numero_suivi      = models.CharField(max_length=100, blank=True, verbose_name="Numéro de suivi")

    class Meta:
        verbose_name        = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering            = ['-dateCde', '-id']

    def __str__(self):
        return f'Commande #{self.id} — {self.dateCde}'

    def can_be_cancelled_by_client(self):
        """Client can cancel only while still pending."""
        return self.status == 'en_attente'

    def compute_total(self):
        """Recompute total from CommandeLigne rows."""
        result = self.lignes.aggregate(total=Sum('sous_total'))['total']
        return result or self.totalCde


# ──────────────────────────────────────────────────────────────
# CommandeLigne  (Order line — one row per product per order)
# ──────────────────────────────────────────────────────────────
class CommandeLigne(models.Model):
    commande      = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit       = models.ForeignKey(Produit,  on_delete=models.PROTECT, related_name='lignes_commande')
    quantite      = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)  # price snapshot at order time
    sous_total    = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name        = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'

    def save(self, *args, **kwargs):
        self.sous_total = self.prix_unitaire * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Commande #{self.commande_id} — {self.produit.libelle} × {self.quantite}'


# ──────────────────────────────────────────────────────────────
# BonDeCommande  (Purchase Order sent to supplier)
# ──────────────────────────────────────────────────────────────
class BonDeCommande(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoye',    'Envoyé au fournisseur'),
        ('accepte',   'Accepté'),
        ('recu',      'Reçu en magasin'),
        ('annule',    'Annulé'),
    ]

    fournisseur   = models.ForeignKey(Fournisseur, on_delete=models.PROTECT, related_name='bons_de_commande')
    commande      = models.ForeignKey(Commande, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='bons_de_commande',
                                      verbose_name="Commande client liée (optionnel)")
    cree_par      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bons_crees')
    statut        = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_envoi    = models.DateTimeField(null=True, blank=True)
    date_reception = models.DateTimeField(null=True, blank=True)
    notes         = models.TextField(blank=True)
    reference     = models.CharField(max_length=50, blank=True, verbose_name="Référence BDC")

    class Meta:
        verbose_name        = 'Bon de Commande'
        verbose_name_plural = 'Bons de Commande'
        ordering            = ['-date_creation']

    def __str__(self):
        return f'BDC #{self.id} — {self.fournisseur.nom} [{self.get_statut_display()}]'

    def save(self, *args, **kwargs):
        if not self.reference:
            super().save(*args, **kwargs)
            self.reference = f'BDC-{self.date_creation.year}-{self.id:04d}'
            BonDeCommande.objects.filter(pk=self.pk).update(reference=self.reference)
        else:
            super().save(*args, **kwargs)

    @property
    def total_bdc(self):
        return sum(ligne.total_ligne for ligne in self.lignes.all())


class BonDeCommandeLigne(models.Model):
    bon        = models.ForeignKey(BonDeCommande, on_delete=models.CASCADE, related_name='lignes')
    produit    = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite   = models.PositiveIntegerField(default=1)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_ligne(self):
        prix = self.prix_achat if self.prix_achat > 0 else self.produit.prix_achat
        return self.quantite * prix

    def __str__(self):
        return f'{self.produit.libelle} × {self.quantite}'


# ──────────────────────────────────────────────────────────────
# Notification  (In-app alerts for admin and clients)
# ──────────────────────────────────────────────────────────────
class Notification(models.Model):
    TYPE_CHOICES = [
        ('nouvelle_commande',  'Nouvelle commande'),
        ('statut_commande',    'Changement de statut'),
        ('stock_bas',          'Stock bas'),
        ('bdc_accepte',        'BDC accepté'),
        ('bdc_recu',           'BDC reçu'),
        ('commande_annulee',   'Commande annulée'),
    ]

    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='magasin_notifications')
    type         = models.CharField(max_length=30, choices=TYPE_CHOICES)
    titre        = models.CharField(max_length=200)
    message      = models.TextField()
    lien         = models.CharField(max_length=500, blank=True)
    lu           = models.BooleanField(default=False)
    cree_le      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering            = ['-cree_le']

    def __str__(self):
        return f'[{self.get_type_display()}] → {self.destinataire.username}'


# ──────────────────────────────────────────────────────────────
# Wishlist
# ──────────────────────────────────────────────────────────────
class Wishlist(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    produit  = models.ForeignKey(Produit, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'produit')
        ordering        = ['-added_at']

    def __str__(self):
        return f'{self.user.username} - {self.produit.libelle}'


# ──────────────────────────────────────────────────────────────
# Review
# ──────────────────────────────────────────────────────────────
class Review(models.Model):
    produit    = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating     = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('produit', 'user')
        ordering        = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.produit.libelle} - {self.rating}★'