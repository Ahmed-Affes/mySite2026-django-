"""
magasin/forms.py  —  All forms used in the app
"""

from django import forms
from .models import Fournisseur, Produit


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
    """Create / Edit a product — used by Admin in Django admin or custom views."""

    class Meta:
        model  = Produit
        fields = ['type', 'libelle', 'description', 'prix', 'stock', 'is_active', 'categorie', 'fournisseur', 'image']
        widgets = {
            'type':        forms.Select(attrs={'class': 'form-select'}),
            'libelle':     forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Nom du produit',
            }),
            'description': forms.Textarea(attrs={
                'class':       'form-control',
                'placeholder': 'Description du produit',
                'rows':        3,
            }),
            'prix':        forms.NumberInput(attrs={
                'class':       'form-control',
                'placeholder': '0.00',
                'step':        '0.01',
                'min':         '0',
            }),
            'stock':       forms.NumberInput(attrs={
                'class':       'form-control',
                'placeholder': '0',
                'min':         '0',
            }),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'categorie':   forms.Select(attrs={'class': 'form-select'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'image':       forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'type':        'Type de produit',
            'libelle':     'Nom',
            'description': 'Description',
            'prix':        'Prix (DT)',
            'stock':       'Stock',
            'is_active':   'Actif',
            'categorie':   'Catégorie',
            'fournisseur': 'Fournisseur',
            'image':       'Image',
        }

    def clean_prix(self):
        prix = self.cleaned_data.get('prix')
        if prix is not None and prix < 0:
            raise forms.ValidationError('Le prix ne peut pas être négatif.')
        return prix