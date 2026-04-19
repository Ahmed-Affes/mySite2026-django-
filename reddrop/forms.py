from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Donneur, Hopital, DemandeUrgente, Campagne, ReponseAppel, BLOOD_TYPE_CHOICES, GENDER_CHOICES

BLOOD_CLASS = 'form-control'
BLOOD_ATTRS = {'class': BLOOD_CLASS, 'style': 'border-radius: 12px; padding: 0.75rem 1rem;'}
SELECT_ATTRS = {'class': 'form-select', 'style': 'border-radius: 12px; padding: 0.75rem 1rem;'}


class DonneurRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=BLOOD_ATTRS))
    groupe_sanguin = forms.ChoiceField(choices=BLOOD_TYPE_CHOICES, widget=forms.Select(attrs=SELECT_ATTRS))
    sexe = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs=SELECT_ATTRS))
    date_naissance = forms.DateField(widget=forms.DateInput(attrs={**BLOOD_ATTRS, 'type': 'date'}))
    ville = forms.CharField(max_length=100, widget=forms.TextInput(attrs=BLOOD_ATTRS))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'groupe_sanguin', 'sexe', 'date_naissance', 'ville']
        widgets = {
            'username': forms.TextInput(attrs=BLOOD_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(BLOOD_ATTRS)
        self.fields['password2'].widget.attrs.update(BLOOD_ATTRS)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Donneur.objects.create(
                user=user,
                groupe_sanguin=self.cleaned_data['groupe_sanguin'],
                sexe=self.cleaned_data['sexe'],
                date_naissance=self.cleaned_data['date_naissance'],
                ville=self.cleaned_data['ville'],
            )
        return user


class HopitalRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=BLOOD_ATTRS))
    nom = forms.CharField(max_length=150, widget=forms.TextInput(attrs=BLOOD_ATTRS))
    adresse = forms.CharField(widget=forms.Textarea(attrs={**BLOOD_ATTRS, 'rows': 3}))
    ville = forms.CharField(max_length=100, widget=forms.TextInput(attrs=BLOOD_ATTRS))
    numero_agrement = forms.CharField(max_length=50, widget=forms.TextInput(attrs=BLOOD_ATTRS))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'nom', 'adresse', 'ville', 'numero_agrement']
        widgets = {
            'username': forms.TextInput(attrs=BLOOD_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(BLOOD_ATTRS)
        self.fields['password2'].widget.attrs.update(BLOOD_ATTRS)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Hopital.objects.create(
                user=user,
                nom=self.cleaned_data['nom'],
                adresse=self.cleaned_data['adresse'],
                ville=self.cleaned_data['ville'],
                numero_agrement=self.cleaned_data['numero_agrement'],
            )
        return user


class DemandeUrgenteForm(forms.ModelForm):
    class Meta:
        model = DemandeUrgente
        fields = ['groupe_sanguin', 'quantite', 'delai', 'ville', 'description']
        widgets = {
            'groupe_sanguin': forms.Select(attrs=SELECT_ATTRS),
            'quantite': forms.NumberInput(attrs=BLOOD_ATTRS),
            'delai': forms.NumberInput(attrs=BLOOD_ATTRS),
            'ville': forms.TextInput(attrs=BLOOD_ATTRS),
            'description': forms.Textarea(attrs={**BLOOD_ATTRS, 'rows': 4}),
        }


class CampagneForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={**BLOOD_ATTRS, 'type': 'date'}))

    class Meta:
        model = Campagne
        fields = ['nom', 'date', 'lieu', 'groupes_cibles', 'capacite_totale']
        widgets = {
            'nom': forms.TextInput(attrs=BLOOD_ATTRS),
            'lieu': forms.TextInput(attrs=BLOOD_ATTRS),
            'groupes_cibles': forms.TextInput(attrs={**BLOOD_ATTRS, 'placeholder': 'Ex: A+, O-, AB+'}),
            'capacite_totale': forms.NumberInput(attrs=BLOOD_ATTRS),
        }


class ReponseAppelForm(forms.ModelForm):
    class Meta:
        model = ReponseAppel
        fields = ['commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={**BLOOD_ATTRS, 'rows': 3, 'placeholder': 'Votre disponibilité, questions...'}),
        }
