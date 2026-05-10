from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum, F
from django.utils import timezone
from functools import wraps
from django.db import transaction

from .models import (
    Produit, Categorie, Fournisseur, Commande, CommandeLigne, 
    Wishlist, Review, BonDeCommande, BonDeCommandeLigne, Notification,
    ProduitFournisseur
)
from .forms import (
    FournisseurForm, ProduitForm, CommandeStatusForm, 
    CommandeAnnulationForm, BonDeCommandeForm, BonDeCommandeLigneFormSet,
    ProfileForm, CommandeFilterForm, ProduitFournisseurFormSet
)
from .views_roles import employe_required, admin_required, is_employe

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

# ── DECORATORS ──────────────────────────────────────────────────────────

def login_required(view_func):
    """Magasin-specific login decorator - always redirects to magasin login"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            path = request.get_full_path()
            return redirect(f'/magasin/login/?next={path}')
        return view_func(request, *args, **kwargs)
    return wrapper

# ── AUTHENTICATION ──────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get('next', 'index')
        return redirect(next_url)
    return render(request, 'magasin/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Bienvenue {user.username} ! Votre compte a été créé.')
        return redirect('index')
    return render(request, 'register.html', {'form': form})

def home_view(request):
    return render(request, 'home.html')

# ── CATALOGUE & PRODUCTS ──────────────────────────────────────────────

@login_required
def index(request):
    queryset = Produit.objects.select_related('categorie').filter(is_active=True)
    search = request.GET.get('search', '').strip()
    if search:
        queryset = queryset.filter(Q(libelle__icontains=search) | Q(description__icontains=search))
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        queryset = queryset.filter(categorie_id=categorie_id)
    
    paginator = Paginator(queryset, 12)
    page_num = request.GET.get('page', 1)
    products = paginator.get_page(page_num)
    categories = Categorie.objects.all()
    return render(request, 'magasin/mesProduits.html', {
        'products': products,
        'categories': categories,
        'search': search,
    })

@login_required
def detail(request, pk):
    product = get_object_or_404(Produit, pk=pk)
    reviews = product.reviews.select_related('user')
    user_review = reviews.filter(user=request.user).first() if request.user.is_authenticated else None
    recommended = Produit.objects.filter(is_active=True).exclude(pk=pk)
    if product.categorie:
        recommended = recommended.filter(categorie=product.categorie)
    recommended = recommended.select_related('categorie')[:10]
    return render(request, 'magasin/detail.html', {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'recommended': recommended,
    })

@employe_required
def produit_create(request):
    form = ProduitForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Produit ajouté au catalogue.")
        return redirect('index')
    return render(request, 'magasin/produit_form.html', {'form': form, 'title': 'Nouveau Produit'})

@employe_required
def produit_edit(request, pk):
    product = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Produit '{product.libelle}' mis à jour.")
        return redirect('detail', pk=pk)
    return render(request, 'magasin/produit_form.html', {'form': form, 'title': 'Modifier Produit'})

@admin_required
@transaction.atomic
def produit_delete(request, pk):
    product = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        name = product.libelle
        product.delete()
        messages.success(request, f"Produit '{name}' supprimé.")
        return redirect('index')
    return render(request, 'magasin/produit_confirm_delete.html', {'product': product})

@employe_required
@transaction.atomic
def produit_sources_manage(request, pk):
    """
    MANAGE SOURCES: Directly link multiple suppliers to a product with pricing.
    """
    product = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        formset = ProduitFournisseurFormSet(request.POST, instance=product)
        if formset.is_valid():
            formset.save()
            messages.success(request, f"Sources d'approvisionnement pour '{product.libelle}' mises à jour.")
            return redirect('detail', pk=product.pk)
    else:
        formset = ProduitFournisseurFormSet(instance=product)
    
    return render(request, 'magasin/produit_sources.html', {
        'product': product,
        'formset': formset
    })

# ── DASHBOARD ─────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    if not is_employe(request.user):
        return render(request, 'magasin/client_dashboard.html')
    
    # Real KPIs for big company usage
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    orders_today = Commande.objects.filter(dateCde=today).count()
    revenue_month = Commande.objects.filter(dateCde__gte=start_of_month).exclude(status='annulee').aggregate(total=Sum('totalCde'))['total'] or 0
    pending_orders = Commande.objects.filter(status='en_attente').count()
    low_stock_count = Produit.objects.filter(stock__lte=F('stock_minimum')).count()
    
    recent_orders = Commande.objects.select_related('client').order_by('-id')[:5]
    low_stock_products = Produit.objects.filter(stock__lte=F('stock_minimum')).order_by('stock')[:5]
    
    # Profit Calculation (delivered orders)
    profit_month = 0
    delivered_lines = CommandeLigne.objects.filter(
        commande__dateCde__gte=start_of_month, 
        commande__status='livree'
    ).select_related('produit')
    for line in delivered_lines:
        profit_month += (line.prix_unitaire - line.produit.prix_achat) * line.quantite

    context = {
        'orders_today': orders_today,
        'revenue_month': revenue_month,
        'profit_month': profit_month,
        'pending_orders': pending_orders,
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'total_products': Produit.objects.count(),
        'total_fournisseurs': Fournisseur.objects.count(),
    }
    return render(request, 'magasin/dashboard.html', context)

# ── CART & ORDERS ─────────────────────────────────────────────────────

@login_required
def panier_voir(request):
    panier_raw = request.session.get('panier', {})
    panier_items = []
    total_panier = 0
    for produit_id_str, quantite in panier_raw.items():
        try:
            produit = Produit.objects.get(pk=int(produit_id_str))
            line_total = produit.prix * quantite
            panier_items.append({
                'produit': produit,
                'quantite': quantite,
                'total': round(line_total, 2),
            })
            total_panier += line_total
        except Produit.DoesNotExist:
            pass
    return render(request, 'magasin/panier.html', {
        'panier_items': panier_items,
        'total_panier': round(total_panier, 2),
    })

@login_required
def panier_ajouter(request, pk):
    if request.method != 'POST': return redirect('index')
    produit = get_object_or_404(Produit, pk=pk)
    
    # Stock Check
    panier = request.session.get('panier', {})
    current_qty = panier.get(str(pk), 0)
    if current_qty + 1 > produit.stock:
        messages.error(request, f"Stock insuffisant pour '{produit.libelle}' ({produit.stock} disponibles).")
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    
    panier[str(pk)] = current_qty + 1
    request.session['panier'] = panier
    request.session.modified = True
    messages.success(request, f"'{produit.libelle}' ajouté au panier.")
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def panier_diminuer(request, pk):
    if request.method != 'POST': return redirect('panier_voir')
    panier = request.session.get('panier', {})
    key = str(pk)
    if key in panier:
        if panier[key] > 1: panier[key] -= 1
        else: del panier[key]
        request.session['panier'] = panier
        request.session.modified = True
    return redirect('panier_voir')

@login_required
def panier_supprimer(request, pk):
    if request.method != 'POST': return redirect('panier_voir')
    panier = request.session.get('panier', {})
    panier.pop(str(pk), None)
    request.session['panier'] = panier
    request.session.modified = True
    messages.info(request, 'Article retiré du panier.')
    return redirect('panier_voir')

@login_required
def panier_vider(request):
    if request.method == 'POST':
        request.session['panier'] = {}
        request.session.modified = True
        messages.info(request, 'Panier vidé.')
    return redirect('panier_voir')

@login_required
@transaction.atomic
def panier_commander(request):
    if request.method != 'POST': return redirect('panier_voir')
    panier_raw = request.session.get('panier', {})
    if not panier_raw:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('panier_voir')

    produits_a_commander = []
    total = 0
    for pid, qty in panier_raw.items():
        produit = get_object_or_404(Produit, pk=int(pid))
        if produit.stock < qty:
            messages.error(request, f"Stock insuffisant pour '{produit.libelle}'.")
            return redirect('panier_voir')
        produits_a_commander.append((produit, qty))
        total += produit.prix * qty

    commande = Commande.objects.create(
        client=request.user,
        status='en_attente',
        totalCde=total,
        dateCde=timezone.now().date(),
        adresse_livraison=request.POST.get('adresse_livraison', ''),
        telephone_contact=request.POST.get('telephone_contact', ''),
        email_contact=request.POST.get('email_contact', '')
    )

    for produit, qty in produits_a_commander:
        CommandeLigne.objects.create(
            commande=commande,
            produit=produit,
            quantite=qty,
            prix_unitaire=produit.prix,
            sous_total=produit.prix * qty
        )
        # We don't deduct stock yet - we do it on confirmation for big companies

    request.session['panier'] = {}
    request.session.modified = True
    
    # Notify Admin
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        Notification.objects.create(
            destinataire=admin,
            type='nouvelle_commande',
            titre=f"Nouvelle commande #{commande.id}",
            message=f"Le client {request.user.username} a passé une commande de {total} DT.",
            lien=f"/magasin/commande/{commande.id}/"
        )

    return render(request, 'magasin/commande_confirmee.html', {'commande': commande})

# ── ORDER MANAGEMENT (ADMIN) ──────────────────────────────────────────

@employe_required
def toutes_commandes(request):
    form = CommandeFilterForm(request.GET or None)
    qs = Commande.objects.select_related('client').prefetch_related('lignes__produit').order_by('-dateCde', '-id')
    
    if form.is_valid():
        if form.cleaned_data.get('status'):
            qs = qs.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('search'):
            search = form.cleaned_data['search']
            qs = qs.filter(Q(id__icontains=search) | Q(client__username__icontains=search))
        if form.cleaned_data.get('date_debut'):
            qs = qs.filter(dateCde__gte=form.cleaned_data['date_debut'])
        if form.cleaned_data.get('date_fin'):
            qs = qs.filter(dateCde__lte=form.cleaned_data['date_fin'])

    paginator = Paginator(qs, 15)
    commandes = paginator.get_page(request.GET.get('page'))
    return render(request, 'magasin/toutes_commandes.html', {'commandes': commandes, 'filter_form': form})

@login_required
def commande_detail(request, pk):
    if is_employe(request.user):
        commande = get_object_or_404(Commande, pk=pk)
        status_form = CommandeStatusForm(initial={
            'status': commande.status, 
            'note_admin': commande.note_admin,
            'numero_suivi': commande.numero_suivi,
            'raison_annulation': commande.raison_annulation
        })
    else:
        commande = get_object_or_404(Commande, pk=pk, client=request.user)
        status_form = None
    
    return render(request, 'magasin/commande_detail.html', {
        'commande': commande,
        'status_form': status_form,
        'can_cancel': commande.can_be_cancelled_by_client()
    })

@employe_required
@transaction.atomic
def update_commande_status(request, pk):
    if request.method != 'POST': return redirect('commande_detail', pk=pk)
    commande = get_object_or_404(Commande, pk=pk)
    form = CommandeStatusForm(request.POST)
    if form.is_valid():
        old_status = commande.status
        new_status = form.cleaned_data['status']
        
        # STOCK LOGIC: Deduct when confirmed, Restore when cancelled
        if new_status == 'confirmee' and old_status == 'en_attente':
            for ligne in commande.lignes.all():
                if ligne.produit.stock < ligne.quantite:
                    messages.error(request, f"Stock insuffisant pour '{ligne.produit.libelle}'.")
                    return redirect('commande_detail', pk=pk)
                ligne.produit.stock -= ligne.quantite
                ligne.produit.save()
                # Notification if low stock
                if ligne.produit.is_low_stock:
                    Notification.objects.create(
                        destinataire=request.user,
                        type='stock_bas',
                        titre="Alerte Stock Bas",
                        message=f"Le stock de '{ligne.produit.libelle}' est de {ligne.produit.stock}.",
                        lien=f"/magasin/produit/{ligne.produit.id}/"
                    )
            commande.date_confirmation = timezone.now()

        elif new_status == 'annulee' and old_status in ['confirmee', 'en_preparation', 'expediee']:
            for ligne in commande.lignes.all():
                ligne.produit.stock += ligne.quantite
                ligne.produit.save()
        
        commande.status = new_status
        commande.note_admin = form.cleaned_data.get('note_admin', '')
        commande.raison_annulation = form.cleaned_data.get('raison_annulation', '')
        commande.numero_suivi = form.cleaned_data.get('numero_suivi', '')
        
        if new_status == 'expediee': commande.date_expedition = timezone.now()
        if new_status == 'livree': commande.date_livraison = timezone.now()
        
        commande.save()
        
        # Notify Client
        Notification.objects.create(
            destinataire=commande.client,
            type='statut_commande',
            titre=f"Mise à jour Commande #{commande.id}",
            message=f"Le statut de votre commande est maintenant: {commande.get_status_display()}.",
            lien=f"/magasin/commande/{commande.id}/"
        )
        messages.success(request, f"Statut de la commande #{pk} mis à jour.")
    return redirect('commande_detail', pk=pk)

@login_required
@transaction.atomic
def client_annuler_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk, client=request.user)
    if not commande.can_be_cancelled_by_client():
        messages.error(request, "Cette commande ne peut plus être annulée.")
        return redirect('commande_detail', pk=pk)
    
    if request.method == 'POST':
        form = CommandeAnnulationForm(request.POST)
        if form.is_valid():
            commande.status = 'annulee'
            commande.raison_annulation = f"Annulée par le client: {form.cleaned_data['raison']}"
            commande.save()
            
            # Notify Admin
            for admin in User.objects.filter(is_superuser=True):
                Notification.objects.create(
                    destinataire=admin,
                    type='commande_annulee',
                    titre=f"Commande #{commande.id} ANNULÉE",
                    message=f"Le client {request.user.username} a annulé sa commande.",
                    lien=f"/magasin/commande/{commande.id}/"
                )
            messages.info(request, "Votre commande a été annulée.")
            return redirect('mes_commandes')
    else:
        form = CommandeAnnulationForm()
    return render(request, 'magasin/commande_annuler.html', {'commande': commande, 'form': form})

@employe_required
@transaction.atomic
def commande_generer_bdc(request, pk):
    """
    SMART FULFILLMENT: Automatically generate BDCs from a client order.
    Groups order lines by supplier and creates a PO for each one.
    """
    commande = get_object_or_404(Commande, pk=pk)
    lignes = commande.lignes.all().select_related('produit')
    
    if not lignes.exists():
        messages.error(request, "Cette commande est vide.")
        return redirect('commande_detail', pk=pk)

    if BonDeCommande.objects.filter(commande=commande).exists():
        messages.warning(request, "Des BDCs existent déjà pour cette commande.")
        return redirect('commande_detail', pk=pk)

    # Group items by supplier
    by_supplier = {}
    missing_suppliers = []
    
    for ligne in lignes:
        supplier = ligne.produit.meilleur_fournisseur
        if not supplier:
            missing_suppliers.append(ligne.produit.libelle)
            continue 
        if supplier not in by_supplier:
            by_supplier[supplier] = []
        by_supplier[supplier].append(ligne)

    if not by_supplier and missing_suppliers:
        messages.error(request, f"Erreur : Impossible de générer des BDCs. Les produits suivants n'ont aucun fournisseur configuré : {', '.join(set(missing_suppliers))}. Veuillez les configurer dans l'administration.")
        return redirect('commande_detail', pk=pk)

    bdc_count = 0
    for supplier, order_lines in by_supplier.items():
        bdc = BonDeCommande.objects.create(
            fournisseur=supplier,
            commande=commande,
            cree_par=request.user,
            statut='brouillon',
            notes=f"Auto-généré pour la commande client #{commande.id}."
        )
        for line in order_lines:
            # Use the specific price from the ProduitFournisseur link
            source = ProduitFournisseur.objects.filter(produit=line.produit, fournisseur=supplier).first()
            prix = source.prix_achat if source else line.produit.prix_achat
            
            BonDeCommandeLigne.objects.create(
                bon=bdc, produit=line.produit,
                quantite=line.quantite, prix_achat=prix
            )
        bdc_count += 1

    if bdc_count > 0:
        messages.success(request, f"Succès : {bdc_count} Bon(s) de commande ont été générés.")
        if missing_suppliers:
            messages.warning(request, f"Attention : Les articles suivants ont été ignorés car ils n'ont pas de fournisseur : {', '.join(set(missing_suppliers))}")
    else:
        messages.info(request, "Aucun Bon de commande n'a été généré.")
        
    return redirect('commande_detail', pk=pk)

# ── PURCHASE ORDERS (BON DE COMMANDE) ──────────────────────────────────

@employe_required
def bdc_liste(request):
    bdcs = BonDeCommande.objects.select_related('fournisseur', 'cree_par').order_by('-date_creation')
    return render(request, 'magasin/bdc_liste.html', {'bdcs': bdcs})

@employe_required
@transaction.atomic
def bdc_create(request):
    if request.method == 'POST':
        form = BonDeCommandeForm(request.POST)
        formset = BonDeCommandeLigneFormSet(request.POST, prefix='lignes')
        if form.is_valid() and formset.is_valid():
            bdc = form.save(commit=False)
            bdc.cree_par = request.user
            bdc.save()
            formset.instance = bdc
            formset.save()
            messages.success(request, f"Bon de commande {bdc.reference} créé.")
            return redirect('bdc_liste')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        # Pre-fill if linked to a low stock product
        pid = request.GET.get('produit')
        initial_data = []
        initial_header = {}
        if pid:
            p = get_object_or_404(Produit, pk=pid)
            initial_data = [{'produit': p, 'quantite': p.stock_minimum * 2}]
            initial_header = {'fournisseur': p.meilleur_fournisseur}
        
        form = BonDeCommandeForm(initial=initial_header)
        formset = BonDeCommandeLigneFormSet(initial=initial_data, prefix='lignes')
    return render(request, 'magasin/bdc_form.html', {'form': form, 'formset': formset})

@employe_required
def bdc_print(request, pk):
    """
    PROFESSIONAL PDF-LIKE VIEW: A clean, minimalist view designed for printing/saving as PDF.
    """
    bdc = get_object_or_404(BonDeCommande, pk=pk)
    return render(request, 'magasin/bdc_print.html', {'bdc': bdc})

@employe_required
def bdc_status_update(request, pk, status):
    bdc = get_object_or_404(BonDeCommande, pk=pk)
    old_status = bdc.statut
    bdc.statut = status

    if status == 'envoye':
        bdc.date_envoi = timezone.now()

    if status == 'recu' and old_status != 'recu':
        bdc.date_reception = timezone.now()
        for ligne in bdc.lignes.all():
            ligne.produit.stock += ligne.quantite
            ligne.produit.save()
            # Notify admins if product is STILL low stock after restock
            if ligne.produit.is_low_stock:
                for admin in User.objects.filter(is_superuser=True):
                    Notification.objects.create(
                        destinataire=admin,
                        type='stock_bas',
                        titre=f"Stock encore bas: {ligne.produit.libelle}",
                        message=(
                            f"Après réception du BDC {bdc.reference}, le stock de "
                            f"'{ligne.produit.libelle}' est {ligne.produit.stock} "
                            f"(minimum: {ligne.produit.stock_minimum}). Commandez davantage."
                        ),
                        lien=f"/magasin/produit/{ligne.produit.id}/"
                    )
        messages.success(request, f"✅ Stock mis à jour suite à la réception du BDC {bdc.reference}.")

    bdc.save()
    if status != 'recu':
        messages.info(request, f"Statut du BDC {bdc.reference} → {bdc.get_statut_display()}.")
    return redirect('bdc_liste')

# ── NOTIFICATIONS ─────────────────────────────────────────────────────

@login_required
def notifications_liste(request):
    notifs = request.user.magasin_notifications.all()
    notifs.filter(lu=False).update(lu=True)
    return render(request, 'magasin/notifications.html', {'notifications': notifs})

# ── PROFILE & OTHER ──────────────────────────────────────────────────

@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour.")
        return redirect('profile')
    return render(request, 'magasin/profile.html', {'form': form})

@login_required
def mes_commandes(request):
    commandes = Commande.objects.filter(client=request.user).prefetch_related('lignes__produit').order_by('-dateCde')
    return render(request, 'magasin/mes_commandes.html', {'commandes': commandes})

class FournisseurListView(ListView):
    model = Fournisseur
    template_name = 'magasin/fournisseurs.html'
    context_object_name = 'fournisseurs'
    paginate_by = 10

    def get_queryset(self):
        qs = Fournisseur.objects.annotate(produits_count=Count('produits_proposes'))
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(nom__icontains=search) | Q(email__icontains=search) | Q(adresse__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '').strip()
        context['total_fournisseurs'] = Fournisseur.objects.count()
        context['total_products'] = Produit.objects.count()
        context['derniere_activite'] = Fournisseur.objects.order_by('-id').first().nom if Fournisseur.objects.exists() else None
        return context

@method_decorator(employe_required, name='dispatch')
class FournisseurCreateView(CreateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'magasin/fournisseur_form.html'
    success_url = reverse_lazy('fournisseurs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouveau fournisseur'
        context['submit_label'] = 'Ajouter'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Fournisseur ajouté.')
        return super().form_valid(form)

@method_decorator(employe_required, name='dispatch')
class FournisseurUpdateView(UpdateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'magasin/fournisseur_form.html'
    success_url = reverse_lazy('fournisseurs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Modifier : {self.object.nom}'
        context['submit_label'] = 'Enregistrer'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Fournisseur «{self.object.nom}» modifié.')
        return super().form_valid(form)

@method_decorator(admin_required, name='dispatch')
class FournisseurDeleteView(DeleteView):
    model = Fournisseur
    template_name = 'magasin/fournisseur_confirm_delete.html'
    success_url = reverse_lazy('fournisseurs')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Fournisseur supprimé.')
        return super().delete(request, *args, **kwargs)

@method_decorator(employe_required, name='dispatch')
class FournisseurDetailView(DetailView):
    model = Fournisseur
    template_name = 'magasin/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Produit.objects.filter(fournisseurs=self.object).select_related('categorie')
        context['bdcs'] = BonDeCommande.objects.filter(fournisseur=self.object).order_by('-date_creation')[:5]
        return context

@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('produit')
    return render(request, 'magasin/wishlist.html', {'wishlist_items': items})

@login_required
def wishlist_add(request, pk):
    if request.method == 'POST':
        produit = get_object_or_404(Produit, pk=pk)
        Wishlist.objects.get_or_create(user=request.user, produit=produit)
        messages.success(request, f'«{produit.libelle}» ajouté aux favoris.')
    return redirect('index')

@login_required
def wishlist_remove(request, pk):
    if request.method == 'POST':
        item = get_object_or_404(Wishlist, pk=pk, user=request.user)
        item.delete()
        messages.success(request, 'Retiré des favoris.')
    return redirect('wishlist')

@login_required
def review_add(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    rating = request.POST.get('rating')
    if rating:
        Review.objects.update_or_create(
            user=request.user, produit=produit,
            defaults={'rating': int(rating), 'comment': request.POST.get('comment', '')}
        )
        messages.success(request, 'Avis enregistré.')
    return redirect('detail', pk=pk)