"""
magasin/forms.py  —  All forms used in the app (enterprise edition)
"""

from django import forms
from django.contrib.auth.models import User
from .models import Fournisseur, Produit, Commande, BonDeCommande, BonDeCommandeLigne, ProduitFournisseur


class FournisseurForm(forms.ModelForm):
    """Create / Edit a supplier."""

    class Meta:
        model  = Fournisseur
        fields = ['nom', 'email', 'telephone', 'adresse']
        widgets = {
            'nom':       forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Nom du fournisseur',
            }),
            'email':     forms.EmailInput(attrs={
                'class':       'form-control',
                'placeholder': 'email@exemple.com',
            }),
            'telephone': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': '8 chiffres',
                'maxlength':   '8',
            }),
            'adresse':   forms.Textarea(attrs={
                'class':       'form-control',
                'placeholder': 'Adresse complète',
                'rows':        3,
            }),
        }
        labels = {
            'nom':       'Nom',
            'email':     'Email',
            'telephone': 'Téléphone',
            'adresse':   'Adresse',
        }

    def clean_telephone(self):
        tel = self.cleaned_data.get('telephone', '').strip()
        if not tel.isdigit():
            raise forms.ValidationError('Le téléphone doit contenir uniquement des chiffres.')
        if len(tel) != 8:
            raise forms.ValidationError('Le téléphone doit contenir exactement 8 chiffres.')
        return tel


class ProduitForm(forms.ModelForm):
    """Create / Edit a product — used by Admin/Employé in the frontend."""

    class Meta:
        model  = Produit
        fields = ['type', 'libelle', 'description', 'prix', 'stock', 'stock_minimum',
                  'is_active', 'categorie', 'image']
        widgets = {
            'type':          forms.Select(attrs={'class': 'form-select tom-select'}),
            'libelle':       forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Nom du produit',
            }),
            'description':   forms.Textarea(attrs={
                'class':       'form-control',
                'placeholder': 'Description du produit',
                'rows':        3,
            }),
            'prix':          forms.NumberInput(attrs={
                'class':       'form-control',
                'placeholder': '0.00',
                'step':        '0.01',
                'min':         '0',
            }),
            'stock':         forms.NumberInput(attrs={
                'class':       'form-control',
                'placeholder': '0',
                'min':         '0',
            }),
            'stock_minimum': forms.NumberInput(attrs={
                'class':       'form-control',
                'placeholder': '5',
                'min':         '0',
            }),
            'is_active':     forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'categorie':     forms.Select(attrs={'class': 'form-select tom-select'}),
            'image':         forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'type':          'Type de produit',
            'libelle':       'Nom',
            'description':   'Description',
            'prix':          'Prix (DT)',
            'stock':         'Stock actuel',
            'stock_minimum': 'Seuil d\'alerte stock',
            'is_active':     'Actif',
            'categorie':     'Catégorie',
            'fournisseur':   'Fournisseur',
            'image':         'Image',
        }

    def clean_prix(self):
        prix = self.cleaned_data.get('prix')
        if prix is not None and prix < 0:
            raise forms.ValidationError('Le prix ne peut pas être négatif.')
        return prix


class CommandeStatusForm(forms.Form):
    """Admin form to update order status with an optional note."""
    status = forms.ChoiceField(
        choices=Commande.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select tom-select'})
    )
    note_admin = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Note interne (facultatif)…',
        }),
        label='Note interne'
    )
    raison_annulation = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Raison de l\'annulation (visible par le client)…',
        }),
        label="Raison d'annulation"
    )
    numero_suivi = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: TN123456789FR',
        }),
        label='Numéro de suivi'
    )


class CommandeAnnulationForm(forms.Form):
    """Client form to cancel their own order."""
    raison = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Expliquez brièvement pourquoi vous souhaitez annuler cette commande…',
        }),
        label='Raison de l\'annulation'
    )


class BonDeCommandeForm(forms.ModelForm):
    """Create a purchase order (BDC) to a supplier."""

    class Meta:
        model  = BonDeCommande
        fields = ['fournisseur', 'commande', 'notes']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select tom-select'}),
            'commande':    forms.Select(attrs={'class': 'form-select tom-select'}),
            'notes':       forms.Textarea(attrs={
                'class':       'form-control',
                'rows':        3,
                'placeholder': 'Instructions ou remarques pour le fournisseur…',
            }),
        }
        labels = {
            'fournisseur': 'Fournisseur',
            'commande':    'Commande client liée (optionnel)',
            'notes':       'Notes',
        }


class BonDeCommandeLigneForm(forms.ModelForm):
    class Meta:
        model  = BonDeCommandeLigne
        fields = ['produit', 'quantite', 'prix_achat']
        widgets = {
            'produit':    forms.Select(attrs={'class': 'form-select tom-select'}),
            'quantite':   forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'produit':    'Produit',
            'quantite':   'Quantité',
            'prix_achat': 'Prix d\'achat unitaire (DT)',
        }


BonDeCommandeLigneFormSet = forms.inlineformset_factory(
    BonDeCommande,
    BonDeCommandeLigne,
    form=BonDeCommandeLigneForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ProfileForm(forms.ModelForm):
    """Client profile update form."""
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'}),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name':  'Nom',
            'email':      'Email',
        }


class CommandeFilterForm(forms.Form):
    """Filter form for admin orders list."""
    STATUS_CHOICES_FILTER = [('', 'Tous les statuts')] + list(Commande.STATUS_CHOICES)

    status     = forms.ChoiceField(choices=STATUS_CHOICES_FILTER, required=False,
                                   widget=forms.Select(attrs={'class': 'form-select form-select-sm tom-select'}))
    search     = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={
                                     'class': 'form-control form-control-sm',
                                     'placeholder': 'Client ou #ID…',
                                 }))
    date_debut = forms.DateField(required=False,
                                 widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
                                 label='Du')
    date_fin   = forms.DateField(required=False,
                                 widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
                                 label='Au')

class ProduitFournisseurForm(forms.ModelForm):
    class Meta:
        model = ProduitFournisseur
        fields = ['fournisseur', 'prix_achat', 'delai_livraison_jours', 'is_preferred']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select tom-select'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'delai_livraison_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_preferred': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

ProduitFournisseurFormSet = forms.inlineformset_factory(
    Produit, ProduitFournisseur, 
    form=ProduitFournisseurForm, 
    extra=1, 
    can_delete=True
)