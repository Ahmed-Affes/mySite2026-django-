from django.conf import settings
from django.db import models
from datetime import timedelta, date
from django.utils import timezone

BLOOD_TYPE_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]
GENDER_CHOICES = [
    ('M', 'Homme'),
    ('F', 'Femme'),
]
RESPONSE_STATUS = [
    ('P', 'En attente'),
    ('C', 'Confirmé'),
    ('R', 'Refusé'),
]


def default_next_date(sexe, last_date=None):
    if not last_date:
        return date.today()
    days = 56 if sexe == 'M' else 84
    return last_date + timedelta(days=days)


class Donneur(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donneur_banque')
    groupe_sanguin = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    sexe = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_naissance = models.DateField()
    ville = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)
    dernier_don = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Donneur {self.user.username} ({self.groupe_sanguin})"

    def prochain_don(self):
        if self.dernier_don:
            next_date = default_next_date(self.sexe, self.dernier_don)
            return max(next_date, date.today())
        return date.today()

    def est_eligible(self):
        return date.today() >= self.prochain_don()


class Hopital(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hopital_banque')
    nom = models.CharField(max_length=150)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    numero_agrement = models.CharField(max_length=50)
    valide = models.BooleanField(default=False)

    def __str__(self):
        return f"Hôpital {self.nom} ({'Validé' if self.valide else 'En attente'})"


class DemandeUrgente(models.Model):
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)
    groupe_sanguin = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    quantite = models.PositiveIntegerField(help_text='Nombre de poches demandées')
    delai = models.PositiveIntegerField(help_text='Délai en jours')
    description = models.TextField()
    ville = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cree_le']

    def __str__(self):
        return f"Demande {self.groupe_sanguin} - {self.quantite} poche(s) par {self.hopital.nom}"


class Campagne(models.Model):
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)
    nom = models.CharField(max_length=150)
    date = models.DateField()
    lieu = models.CharField(max_length=150)
    groupes_cibles = models.CharField(max_length=150, help_text='Ex: A+, O-, AB+')
    capacite_totale = models.PositiveIntegerField()
    places_prises = models.PositiveIntegerField(default=0)
    valide = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Campagne {self.nom} - {self.lieu}"

    def places_restantes(self):
        return max(self.capacite_totale - self.places_prises, 0)


class Don(models.Model):
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE)
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=date.today)
    groupe_sanguin = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    quantite = models.PositiveIntegerField(default=1)
    lieu = models.CharField(max_length=150)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Don de {self.donneur.user.username} le {self.date}"


class ReponseAppel(models.Model):
    demande = models.ForeignKey(DemandeUrgente, on_delete=models.CASCADE)
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE)
    date_reponse = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=1, choices=RESPONSE_STATUS, default='P')
    commentaire = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_reponse']

    def __str__(self):
        return f"Réponse de {self.donneur.user.username} à {self.demande}"


class StockSang(models.Model):
    PRODUIT_CHOICES = [
        ('GR', 'Globules Rouges'),
        ('PL', 'Plaquettes'),
        ('PS', 'Plasma'),
    ]
    STATUT_CHOICES = [
        ('TEST', 'En test'),
        ('OK', 'En stock'),
        ('USED', 'Utilisé'),
        ('EXP', 'Expiré'),
    ]
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name='stocks')
    don = models.OneToOneField('Don', on_delete=models.SET_NULL, null=True, blank=True)
    groupe_sanguin = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    type_produit = models.CharField(max_length=2, choices=PRODUIT_CHOICES, default='GR')
    date_prelevement = models.DateField(default=date.today)
    date_peremption = models.DateField(blank=True)
    statut = models.CharField(max_length=4, choices=STATUT_CHOICES, default='TEST')

    class Meta:
        ordering = ['date_peremption']

    def save(self, *args, **kwargs):
        if not self.date_peremption:
            if self.type_produit == 'GR':
                self.date_peremption = self.date_prelevement + timedelta(days=42)
            elif self.type_produit == 'PL':
                self.date_peremption = self.date_prelevement + timedelta(days=5)
            elif self.type_produit == 'PS':
                self.date_peremption = self.date_prelevement + timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Poche {self.groupe_sanguin} ({self.get_type_produit_display()}) - {self.hopital.nom}"


class RendezVous(models.Model):
    STATUT_CHOICES = [
        ('P', 'Planifié'),
        ('H', 'Honoré'),
        ('A', 'Annulé'),
    ]
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE, related_name='rendezvous')
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name='rendezvous')
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, null=True, blank=True)
    date_heure = models.DateTimeField()
    statut = models.CharField(max_length=1, choices=STATUT_CHOICES, default='P')

    class Meta:
        ordering = ['-date_heure']

    def __str__(self):
        return f"RDV de {self.donneur.user.username} le {self.date_heure}"


class TransfertStock(models.Model):
    STATUT_CHOICES = [
        ('ATT', 'En attente'),
        ('APP', 'Approuvé'),
        ('REJ', 'Rejeté'),
        ('TER', 'Terminé'),
    ]
    hopital_demandeur = models.ForeignKey(Hopital, related_name='transferts_demandes', on_delete=models.CASCADE)
    hopital_fournisseur = models.ForeignKey(Hopital, related_name='transferts_fournis', on_delete=models.CASCADE)
    groupe_sanguin = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    quantite = models.PositiveIntegerField()
    statut = models.CharField(max_length=3, choices=STATUT_CHOICES, default='ATT')
    date_demande = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_demande']

    def __str__(self):
        return f"Transfert {self.quantite}x {self.groupe_sanguin}: {self.hopital_fournisseur.nom} -> {self.hopital_demandeur.nom}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=150)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    lue = models.BooleanField(default=False)
    lien = models.CharField(max_length=255, blank=True, help_text="Lien optionnel vers l'action")

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Notif: {self.titre} pour {self.user.username}"

class Message(models.Model):
    expediteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages_recus')
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lue = models.BooleanField(default=False)

    class Meta:
        ordering = ['date_envoi']

    def __str__(self):
        return f"De {self.expediteur.username} à {self.destinataire.username} ({self.date_envoi})"