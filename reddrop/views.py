from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404

from .forms import (
    DonneurRegistrationForm,
    HopitalRegistrationForm,
    DemandeUrgenteForm,
    CampagneForm,
    ReponseAppelForm,
)
from .models import BLOOD_TYPE_CHOICES, Campagne, DemandeUrgente, Don, ReponseAppel, StockSang, RendezVous, Notification, TransfertStock, Message
from .utils import get_compatible_receivers, get_compatible_donors
from django.db import models


def _is_hopital(request):
    return request.user.is_authenticated and hasattr(request.user, 'hopital_banque')


def _is_donneur(request):
    return request.user.is_authenticated and hasattr(request.user, 'donneur_banque')


def home(request):
    demandes = DemandeUrgente.objects.filter(active=True)[:4]
    campagnes = Campagne.objects.filter(valide=True)[:4]
    return render(request, 'reddrop/home.html', {
        'demandes': demandes,
        'campagnes': campagnes,
        'is_hospital': _is_hopital(request),
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('blood_dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    
    # Add CSS classes to match the theme
    for field in form.fields.values():
        field.widget.attrs.update({
            'class': 'form-control',
            'placeholder': field.label
        })

    if form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Connexion réussie.')
        return redirect('blood_dashboard')

    return render(request, 'reddrop/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous êtes déconnecté.')
    return redirect('blood_home')


def _register(request, form_class, role):
    form = form_class(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Inscription {role.lower()} réussie.')
        return redirect('blood_dashboard')
    return render(request, 'reddrop/register.html', {'form': form, 'role': role})


def register_donneur(request):
    return _register(request, DonneurRegistrationForm, 'Donneur')


def register_hopital(request):
    return _register(request, HopitalRegistrationForm, 'Hôpital')


def urgent_requests(request):
    demandes = DemandeUrgente.objects.filter(active=True)
    groupe = request.GET.get('groupe')
    ville = request.GET.get('ville')

    if groupe:
        demandes = demandes.filter(groupe_sanguin=groupe)
    if ville:
        demandes = demandes.filter(ville__icontains=ville)

    compatible_types = []
    if _is_donneur(request):
        compatible_types = get_compatible_receivers(request.user.donneur_banque.groupe_sanguin)

    return render(request, 'reddrop/urgent_requests.html', {
        'demandes': demandes,
        'groupe': groupe,
        'ville': ville,
        'blood_types': BLOOD_TYPE_CHOICES,
        'can_respond': _is_donneur(request),
        'is_hospital': _is_hopital(request),
        'compatible_types': compatible_types,
    })


def campaigns(request):
    campagnes = Campagne.objects.filter(valide=True)
    return render(request, 'reddrop/campaigns.html', {
        'campagnes': campagnes,
        'can_publish': _is_hopital(request),
    })


@login_required
def publish_request(request):
    if not _is_hopital(request):
        messages.warning(request, 'Seul un compte hôpital peut publier une demande.')
        return redirect('blood_home')

    form = DemandeUrgenteForm(request.POST or None)
    if form.is_valid():
        demande = form.save(commit=False)
        demande.hopital = request.user.hopital_banque
        demande.save()
        messages.success(request, 'Demande urgente publiée.')
        return redirect('blood_demandes')

    return render(request, 'reddrop/request_form.html', {
        'form': form,
        'title': 'Publier une demande urgente',
    })


@login_required
def publish_campaign(request):
    if not _is_hopital(request):
        messages.warning(request, 'Seul un hôpital peut créer une campagne.')
        return redirect('blood_home')

    form = CampagneForm(request.POST or None)
    if form.is_valid():
        campagne = form.save(commit=False)
        campagne.hopital = request.user.hopital_banque
        campagne.places_prises = 0
        campagne.save()
        messages.success(request, 'Campagne créée avec succès.')
        return redirect('blood_campaigns')

    return render(request, 'reddrop/request_form.html', {
        'form': form,
        'title': 'Créer une campagne',
    })


@login_required
def respond_request(request, demande_id):
    if not _is_donneur(request):
        messages.warning(request, 'Seul un donneur peut répondre à une demande.')
        return redirect('blood_home')

    demande = get_object_or_404(DemandeUrgente, pk=demande_id, active=True)
    form = ReponseAppelForm(request.POST or None)
    if form.is_valid():
        reponse = form.save(commit=False)
        reponse.demande = demande
        reponse.donneur = request.user.donneur_banque
        reponse.save()

        # START CONVERSATION: Automatically create a message
        if reponse.commentaire:
            Message.objects.get_or_create(
                expediteur=request.user,
                destinataire=demande.hopital.user,
                contenu=f"[Rponse Urgence {demande.groupe_sanguin}] : {reponse.commentaire}"
            )

        messages.success(request, 'Votre rponse a t enregistre.')
        return redirect('blood_dashboard')

    return render(request, 'reddrop/respond_request.html', {
        'form': form,
        'demande': demande,
    })


@login_required
def participer_campagne(request, campagne_id):
    if not _is_donneur(request):
        messages.warning(request, 'Seul un donneur peut participer à une campagne.')
        return redirect('blood_campaigns')

    campagne = get_object_or_404(Campagne, pk=campagne_id, valide=True)
    donneur = request.user.donneur_banque

    # Check if already registered
    already_reg = RendezVous.objects.filter(donneur=donneur, campagne=campagne).exists()
    if already_reg:
        messages.info(request, 'Vous êtes déjà inscrit à cette campagne.')
        return redirect('blood_dashboard')

    if campagne.places_restantes() > 0:
        # Create appointment
        from django.utils import timezone
        import datetime
        # Simple implementation: set time to 9 AM on the campaign date
        dt = timezone.make_aware(datetime.datetime.combine(campagne.date, datetime.time(9, 0)))
        
        RendezVous.objects.create(
            donneur=donneur,
            hopital=campagne.hopital,
            campagne=campagne,
            date_heure=dt,
            statut='P'
        )
        
        campagne.places_prises += 1
        campagne.save()
        
        messages.success(request, f'Votre participation à "{campagne.nom}" a été enregistrée.')
        return redirect('blood_dashboard')
    else:
        messages.error(request, 'Désolé, cette campagne est complète.')
        return redirect('blood_campaigns')

@login_required
def edit_request(request, pk):
    if not _is_hopital(request):
        return redirect('blood_home')
    demande = get_object_or_404(DemandeUrgente, pk=pk, hopital=request.user.hopital_banque)
    form = DemandeUrgenteForm(request.POST or None, instance=demande)
    if form.is_valid():
        form.save()
        messages.success(request, 'Demande mise à jour.')
        return redirect('blood_dashboard')
    return render(request, 'reddrop/request_form.html', {'form': form, 'title': 'Modifier la demande'})

@login_required
def delete_request(request, pk):
    if not _is_hopital(request):
        return redirect('blood_home')
    demande = get_object_or_404(DemandeUrgente, pk=pk, hopital=request.user.hopital_banque)
    demande.delete()
    messages.success(request, 'Demande supprimée.')
    return redirect('blood_dashboard')

@login_required
def edit_campaign(request, pk):
    if not _is_hopital(request):
        return redirect('blood_home')
    campagne = get_object_or_404(Campagne, pk=pk, hopital=request.user.hopital_banque)
    form = CampagneForm(request.POST or None, instance=campagne)
    if form.is_valid():
        form.save()
        messages.success(request, 'Campagne mise à jour.')
        return redirect('blood_dashboard')
    return render(request, 'reddrop/request_form.html', {'form': form, 'title': 'Modifier la campagne'})

@login_required
def delete_campaign(request, pk):
    if not _is_hopital(request):
        return redirect('blood_home')
    campagne = get_object_or_404(Campagne, pk=pk, hopital=request.user.hopital_banque)
    campagne.delete()
    messages.success(request, 'Campagne supprimée.')
    return redirect('blood_dashboard')

@login_required
def delete_reponse(request, pk):
    """Allow a hospital to dismiss/delete a donor response — also cleans up the linked message thread."""
    if not _is_hopital(request):
        return redirect('blood_home')
    reponse = get_object_or_404(ReponseAppel, pk=pk, demande__hopital=request.user.hopital_banque)
    donor_user = reponse.donneur.user
    hospital_user = request.user
    # Also delete the message conversation between this hospital and the donor
    Message.objects.filter(
        (models.Q(expediteur=hospital_user) & models.Q(destinataire=donor_user)) |
        (models.Q(expediteur=donor_user) & models.Q(destinataire=hospital_user))
    ).delete()
    reponse.delete()
    messages.success(request, 'Réponse et conversation supprimées.')
    return redirect('blood_dashboard')

@login_required
def update_rendezvous_status(request, pk, status):
    if not _is_hopital(request):
        return redirect('blood_home')
    rdv = get_object_or_404(RendezVous, pk=pk, hopital=request.user.hopital_banque)
    if status in ['H', 'A']:
        rdv.statut = status
        rdv.save()
        messages.success(request, f'Statut du rendez-vous mis à jour: {rdv.get_statut_display()}')
    return redirect('blood_dashboard')

@login_required
def cancel_rendezvous(request, pk):
    if _is_donneur(request):
        rdv = get_object_or_404(RendezVous, pk=pk, donneur=request.user.donneur_banque)
    elif _is_hopital(request):
        rdv = get_object_or_404(RendezVous, pk=pk, hopital=request.user.hopital_banque)
    else:
        return redirect('blood_home')
    
    if rdv.campagne:
        rdv.campagne.places_prises = max(0, rdv.campagne.places_prises - 1)
        rdv.campagne.save()
    
    rdv.delete()
    messages.success(request, 'Rendez-vous annulé.')
    return redirect('blood_dashboard')

@login_required
def all_rendezvous(request):
    if _is_donneur(request):
        rdvs = RendezVous.objects.filter(donneur=request.user.donneur_banque)
    elif _is_hopital(request):
        rdvs = RendezVous.objects.filter(hopital=request.user.hopital_banque)
    else:
        return redirect('blood_home')
    return render(request, 'reddrop/all_list.html', {'items': rdvs, 'title': 'Tous mes Rendez-vous', 'type': 'rdv'})

@login_required
def delete_rendezvous(request, pk):
    if _is_donneur(request):
        rdv = get_object_or_404(RendezVous, pk=pk, donneur=request.user.donneur_banque)
    elif _is_hopital(request):
        rdv = get_object_or_404(RendezVous, pk=pk, hopital=request.user.hopital_banque)
    else:
        return redirect('blood_home')
    
    rdv.delete()
    messages.success(request, 'Historique de rendez-vous supprimé.')
    return redirect('all_rendezvous')

@login_required
def delete_don(request, pk):
    if not _is_donneur(request):
        return redirect('blood_home')
    don = get_object_or_404(Don, pk=pk, donneur=request.user.donneur_banque)
    don.delete()
    messages.success(request, 'Historique de don supprimé.')
    return redirect('blood_dashboard')

@login_required
def clear_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, 'Toutes les notifications ont été supprimées.')
    return redirect('blood_dashboard')

@login_required
def all_my_campaigns(request):
    if not _is_hopital(request):
        return redirect('blood_home')
    campagnes = Campagne.objects.filter(hopital=request.user.hopital_banque)
    return render(request, 'reddrop/all_list.html', {'items': campagnes, 'title': 'Toutes mes Campagnes', 'type': 'campagne'})

@login_required
def message_list(request):
    # Get all users the current user has exchanged messages with
    received = Message.objects.filter(destinataire=request.user).values_list('expediteur', flat=True)
    sent = Message.objects.filter(expediteur=request.user).values_list('destinataire', flat=True)
    user_ids = set(received) | set(sent)
    from django.contrib.auth.models import User
    contacts = User.objects.filter(id__in=user_ids)
    return render(request, 'reddrop/message_list.html', {'contacts': contacts})

@login_required
def view_conversation(request, user_id):
    from django.contrib.auth.models import User
    other_user = get_object_or_404(User, id=user_id)
    messages_chat = Message.objects.filter(
        (models.Q(expediteur=request.user) & models.Q(destinataire=other_user)) |
        (models.Q(expediteur=other_user) & models.Q(destinataire=request.user))
    ).order_by('date_envoi')

    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            Message.objects.create(
                expediteur=request.user,
                destinataire=other_user,
                contenu=contenu
            )
            return redirect('view_conversation', user_id=user_id)

    return render(request, 'reddrop/chat.html', {
        'other_user': other_user,
        'messages_chat': messages_chat
    })

@login_required
def delete_conversation(request, user_id):
    from django.contrib.auth.models import User
    other_user = get_object_or_404(User, id=user_id)
    # Delete all messages between these two users
    Message.objects.filter(
        (models.Q(expediteur=request.user) & models.Q(destinataire=other_user)) |
        (models.Q(expediteur=other_user) & models.Q(destinataire=request.user))
    ).delete()
    # Also delete any ReponseAppel linked between these two users (either direction)
    # Case 1: current user is hospital, other_user is donor
    if _is_hopital(request) and hasattr(other_user, 'donneur_banque'):
        ReponseAppel.objects.filter(
            donneur=other_user.donneur_banque,
            demande__hopital=request.user.hopital_banque
        ).delete()
    # Case 2: current user is donor, other_user is hospital
    elif _is_donneur(request) and hasattr(other_user, 'hopital_banque'):
        ReponseAppel.objects.filter(
            donneur=request.user.donneur_banque,
            demande__hopital=other_user.hopital_banque
        ).delete()
    messages.success(request, f'Conversation avec {other_user.username} supprimée.')
    return redirect('message_list')

@login_required
def dashboard(request):
    notifications = Notification.objects.filter(user=request.user, lue=False)

    if _is_donneur(request):
        donneur = request.user.donneur_banque
        compatible_types = get_compatible_receivers(donneur.groupe_sanguin)
        rdvs = RendezVous.objects.filter(donneur=donneur)
        return render(request, 'reddrop/dashboard.html', {
            'type': 'donneur',
            'donneur': donneur,
            'dons': Don.objects.filter(donneur=donneur),
            'reponses': ReponseAppel.objects.filter(donneur=donneur),
            'demandes_compatibles': DemandeUrgente.objects.filter(
                active=True, groupe_sanguin__in=compatible_types
            ),
            'rendezvous': rdvs,
            'notifications': notifications,
        })

    if _is_hopital(request):
        hopital = request.user.hopital_banque
        demandes = DemandeUrgente.objects.filter(hopital=hopital)
        reponses_recues = ReponseAppel.objects.filter(demande__in=demandes)
        rdvs = RendezVous.objects.filter(hopital=hopital)
        return render(request, 'reddrop/dashboard.html', {
            'type': 'hopital',
            'hospital': hopital,
            'demandes': demandes,
            'reponses_recues': reponses_recues,
            'campagnes': Campagne.objects.filter(hopital=hopital),
            'rendezvous': rdvs,
            'notifications': notifications,
        })

    if request.user.is_superuser:
        return redirect('/admin/')

    messages.warning(request, "Votre compte n'est ni configuré en Hôpital ni en Donneur. Veuillez vous déconnecter.")
    return render(request, 'reddrop/dashboard.html', {'type': 'none'})
@login_required
def blood_statistics(request):
    """View to display detailed analytics for both Donors and Hospitals."""
    from django.db.models import Count, Sum, Q
    from django.utils import timezone
    import datetime
    
    stats = {}
    # Reference rarity percentages (Global Average)
    rarity_data = {'O+': 37.4, 'A+': 35.8, 'B+': 8.5, 'O-': 6.6, 'A-': 6.3, 'AB+': 3.4, 'B-': 1.5, 'AB-': 0.6}
    
    if _is_donneur(request):
        donneur = request.user.donneur_banque
        dons = Don.objects.filter(donneur=donneur)
        total_poches = dons.aggregate(total=Sum('quantite'))['total'] or 0
        
        # Calculate rank/badge
        rank = "Nouvel Espoir"
        if total_poches >= 10: rank = "Héros d'Élite"
        elif total_poches >= 5: rank = "Sauveur Régulier"
        elif total_poches >= 1: rank = "Cœur Généreux"

        stats = {
            'role': 'donneur',
            'donneur': donneur,
            'rank': rank,
            'rarity': rarity_data.get(donneur.groupe_sanguin, 5),
            'total_dons': dons.count(),
            'total_poches': total_poches,
            'vies_sauvees': total_poches * 3,
            'volume_total': total_poches * 450,
            'evolution': dons.extra(select={'month': "strftime('%%m', date)"}).values('month').annotate(count=Count('id')).order_by('month'),
            'part_par_lieu': dons.values('lieu').annotate(count=Count('id')),
            'projected_vies': (total_poches + 4) * 3, # Projection if they continue for a year
        }
        
    elif _is_hopital(request):
        hopital = request.user.hopital_banque
        stocks = StockSang.objects.filter(hopital=hopital)
        campagnes = Campagne.objects.filter(hopital=hopital)
        demandes = DemandeUrgente.objects.filter(hopital=hopital)
        
        # Stock Expiry Risk (within 7 days)
        today = datetime.date.today()
        seven_days_later = today + datetime.timedelta(days=7)
        expiry_risk = stocks.filter(date_peremption__lte=seven_days_later, statut='OK').count()
        
        # Donor Loyalty (returning donors)
        all_dons = Don.objects.filter(hopital=hopital)
        total_dons_count = all_dons.count()
        returning_donors = all_dons.values('donneur').annotate(dcount=Count('id')).filter(dcount__gt=1).count()
        loyalty_rate = (returning_donors / total_dons_count * 100) if total_dons_count > 0 else 0
        
        stats = {
            'role': 'hopital',
            'hospital': hopital,
            'stock_total': stocks.count(),
            'expiry_risk': expiry_risk,
            'loyalty_rate': round(loyalty_rate, 1),
            'stock_per_type': stocks.values('groupe_sanguin').annotate(count=Count('id')).order_by('groupe_sanguin'),
            'campaign_count': campagnes.count(),
            'success_rate': round((campagnes.aggregate(s=Sum('places_prises'))['s'] or 0) / (campagnes.aggregate(s=Sum('capacite_totale'))['s'] or 1) * 100, 1),
            'demandes_publiees': demandes.count(),
            'most_requested': demandes.values('groupe_sanguin').annotate(count=Count('id')).order_by('-count')[:4],
        }
    
    return render(request, 'reddrop/statistics.html', {'stats': stats})
