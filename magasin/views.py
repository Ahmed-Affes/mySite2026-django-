from django.shortcuts           import render, get_object_or_404, redirect
from django.contrib.auth        import authenticate, login, logout
from django.contrib.auth.forms  import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib             import messages
from django.core.paginator      import Paginator
from django.core.exceptions     import PermissionDenied
from django.db.models           import Count, Q
from django.utils               import timezone
from functools import wraps

from .models   import Produit, Categorie, Fournisseur, Commande, Wishlist, Review
from .forms    import FournisseurForm
from .views_roles import employe_required, admin_required, is_employe

def login_required(view_func):
    """Magasin-specific login decorator - always redirects to magasin login"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            path = request.get_full_path()
            return redirect(f'/magasin/login/?next={path}')
        return view_func(request, *args, **kwargs)
    return wrapper

def login_view(request):
    """Login page — redirects to 'index' on success."""
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
    """User registration — new users become Clients automatically."""
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


@login_required
def index(request):
    """
    Product catalogue with search, category filter, and pagination.
    Accessible by: Client, Employé, Admin.
    """
    queryset = Produit.objects.select_related('categorie', 'fournisseur').filter(is_active=True)

    search = request.GET.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(libelle__icontains=search) | Q(description__icontains=search)
        )

    categorie_id = request.GET.get('categorie')
    if categorie_id:
        queryset = queryset.filter(categorie_id=categorie_id)

    paginator = Paginator(queryset, 12)
    page_num  = request.GET.get('page', 1)
    products  = paginator.get_page(page_num)

    categories = Categorie.objects.all()

    return render(request, 'magasin/mesProduits.html', {
        'products':   products,
        'categories': categories,
        'search':     search,
    })


@login_required
def detail(request, pk):
    """Single product detail page."""
    product = get_object_or_404(Produit, pk=pk)
    reviews = product.reviews.select_related('user')
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    return render(request, 'magasin/detail.html', {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
    })


@login_required
def dashboard(request):
    """
    Dashboard stats.
    Clients see a simplified version; Employé/Admin see the full stats.
    """
    context = {}

    if is_employe(request.user):
        products_qs  = Produit.objects.select_related('categorie').all()
        recent       = products_qs.order_by('-id')[:6]

        low_stock = products_qs.filter(image='')

        context = {
            'total_products':    products_qs.count(),
            'total_categories':  Categorie.objects.count(),
            'total_fournisseurs': Fournisseur.objects.count(),
            'recent_products':   recent,
            'low_stock':         low_stock,
        }

    return render(request, 'magasin/dashboard.html', context)


@employe_required
def fournisseurs(request):
    """
    Supplier list with search and pagination.
    Accessible by: Employé, Admin.
    """
    qs = Fournisseur.objects.annotate(produits_count=Count('produit'))

    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(
            Q(nom__icontains=search) |
            Q(email__icontains=search) |
            Q(adresse__icontains=search)
        )

    paginator    = Paginator(qs, 10)
    page_num     = request.GET.get('page', 1)
    fournisseurs_page = paginator.get_page(page_num)

    last = Fournisseur.objects.order_by('-id').first()

    return render(request, 'magasin/fournisseurs.html', {
        'fournisseurs':      fournisseurs_page,
        'total_fournisseurs': Fournisseur.objects.count(),
        'total_products':    Produit.objects.count(),
        'derniere_activite': last.nom if last else '—',
        'search':            search,
    })


@employe_required
def fournisseur_create(request):
    """Create a new supplier. Accessible by: Employé, Admin."""
    form = FournisseurForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fournisseur ajouté avec succès.')
        return redirect('fournisseurs')

    return render(request, 'magasin/fournisseur_form.html', {
        'form':         form,
        'title':        'Nouveau fournisseur',
        'submit_label': 'Ajouter',
    })


@employe_required
def fournisseur_edit(request, pk):
    """Edit an existing supplier. Accessible by: Employé, Admin."""
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    form = FournisseurForm(request.POST or None, instance=fournisseur)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Fournisseur «{fournisseur.nom}» modifié.')
        return redirect('fournisseurs')

    return render(request, 'magasin/fournisseur_form.html', {
        'form':         form,
        'title':        f'Modifier : {fournisseur.nom}',
        'submit_label': 'Enregistrer',
    })


@admin_required
def fournisseur_delete(request, pk):
    """
    Delete a supplier.
    GET  → confirmation page.
    POST → actually delete.
    Accessible by: Admin only.
    """
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        nom = fournisseur.nom
        fournisseur.delete()
        messages.success(request, f'Fournisseur «{nom}» supprimé.')
        return redirect('fournisseurs')

    return render(request, 'magasin/fournisseur_confirm_delete.html', {
        'fournisseur': fournisseur,
    })


@login_required
def panier_voir(request):
    """
    Display the cart.
    The cart is stored in the session as:
        request.session['panier'] = { '<product_id>': <quantity>, ... }
    """
    panier_raw  = request.session.get('panier', {})
    panier_items = []
    total_panier = 0

    for produit_id_str, quantite in panier_raw.items():
        try:
            produit = Produit.objects.get(pk=int(produit_id_str))
            line_total = produit.prix * quantite
            panier_items.append({
                'produit':  produit,
                'quantite': quantite,
                'total':    round(line_total, 2),
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
    """
    Add one unit of a product to the cart.
    Accepts POST only; redirects to `next` param or back to catalogue.
    """
    if request.method != 'POST':
        return redirect('index')

    produit = get_object_or_404(Produit, pk=pk)
    panier  = request.session.get('panier', {})

    key = str(pk)
    panier[key] = panier.get(key, 0) + 1
    request.session['panier'] = panier
    request.session.modified  = True

    messages.success(request, f'«{produit.libelle}» ajouté au panier.')

    next_url = request.POST.get('next') or request.GET.get('next') or 'index'
    return redirect(next_url)


@login_required
def panier_diminuer(request, pk):
    """
    Remove one unit of a product from the cart.
    If quantity reaches 0, the item is removed.
    """
    if request.method != 'POST':
        return redirect('panier_voir')

    panier = request.session.get('panier', {})
    key    = str(pk)

    if key in panier:
        if panier[key] > 1:
            panier[key] -= 1
        else:
            del panier[key]
        request.session['panier'] = panier
        request.session.modified  = True

    return redirect('panier_voir')


@login_required
def panier_supprimer(request, pk):
    """Remove a product entirely from the cart."""
    if request.method != 'POST':
        return redirect('panier_voir')

    panier = request.session.get('panier', {})
    key    = str(pk)
    panier.pop(key, None)
    request.session['panier'] = panier
    request.session.modified  = True

    messages.info(request, 'Article retiré du panier.')
    return redirect('panier_voir')


@login_required
def panier_vider(request):
    """Clear the entire cart."""
    if request.method == 'POST':
        request.session['panier'] = {}
        request.session.modified  = True
        messages.info(request, 'Panier vidé.')
    return redirect('panier_voir')


@login_required
def panier_commander(request):
    """
    Confirm the cart → create a Commande in the database.
    POST only.
    """
    if request.method != 'POST':
        return redirect('panier_voir')

    panier_raw = request.session.get('panier', {})
    if not panier_raw:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('panier_voir')

    produits_valides = []
    total = 0
    for produit_id_str, quantite in panier_raw.items():
        try:
            produit = Produit.objects.get(pk=int(produit_id_str))
            produits_valides.append((produit, quantite))
            total += produit.prix * quantite
        except Produit.DoesNotExist:
            pass

    if not produits_valides:
        messages.error(request, 'Aucun produit valide dans le panier.')
        return redirect('panier_voir')


    adresse = request.POST.get('adresse_livraison', '')
    telephone = request.POST.get('telephone_contact', '')
    email = request.POST.get('email_contact', '')

    commande = Commande.objects.create(
        client=request.user,
        status='en_attente',
        totalCde=round(total, 2),
        dateCde=timezone.now().date(),
        adresse_livraison=adresse,
        telephone_contact=telephone,
        email_contact=email,
    )
    for produit, _ in produits_valides:
        commande.produits.add(produit)


    request.session['panier'] = {}
    request.session.modified  = True

    return render(request, 'magasin/commande_confirmee.html', {
        'commande': commande,
    })


@login_required
def minproject_home(request):
    """Redirect to the new BloodConnect platform (minProject)"""
    return redirect('bloodconnect_home')


@login_required
def wishlist_view(request):
    """Display user's wishlist."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('produit')
    return render(request, 'magasin/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def wishlist_add(request, pk):
    """Add product to wishlist."""
    if request.method != 'POST':
        return redirect('index')
    
    produit = get_object_or_404(Produit, pk=pk)
    Wishlist.objects.get_or_create(user=request.user, produit=produit)
    messages.success(request, f'«{produit.libelle}» ajouté à vos favoris.')
    return redirect('index')


@login_required
def wishlist_remove(request, pk):
    """Remove product from wishlist."""
    if request.method != 'POST':
        return redirect('wishlist')
    
    wishlist_item = get_object_or_404(Wishlist, pk=pk, user=request.user)
    produit = wishlist_item.produit
    wishlist_item.delete()
    messages.success(request, f'«{produit.libelle}» retiré des favoris.')
    return redirect('wishlist')


@login_required
def review_add(request, pk):
    """Add or update a review for a product."""
    produit = get_object_or_404(Produit, pk=pk)
    
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '')
    
    if not rating or int(rating) not in range(1, 6):
        messages.error(request, 'Veuillez sélectionner une note.')
        return redirect('detail', pk=pk)
    
    review, created = Review.objects.update_or_create(
        user=request.user,
        produit=produit,
        defaults={'rating': int(rating), 'comment': comment}
    )
    
    if created:
        messages.success(request, 'Avis ajouté avec succès.')
    else:
        messages.success(request, 'Avis mis à jour.')
    return redirect('detail', pk=pk)


@login_required
def mes_commandes(request):
    """Display user's order history."""
    commandes = Commande.objects.filter(client=request.user).prefetch_related('produits').order_by('-dateCde')
    return render(request, 'magasin/mes_commandes.html', {'commandes': commandes})


@login_required
def commande_detail(request, pk):
    """Display order details."""
    if is_employe(request.user) or request.user.is_superuser:
        commande = get_object_or_404(Commande, pk=pk)
    else:
        commande = get_object_or_404(Commande, pk=pk, client=request.user)
    return render(request, 'magasin/commande_detail.html', {'commande': commande})


@employe_required
def toutes_commandes(request):
    """Admin view for all orders."""
    commandes = Commande.objects.select_related('client').prefetch_related('produits').order_by('-dateCde', '-id')
    return render(request, 'magasin/toutes_commandes.html', {'commandes': commandes})

@employe_required
def update_commande_status(request, pk):
    """Admin action to update order status."""
    if request.method == 'POST':
        commande = get_object_or_404(Commande, pk=pk)
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Commande._meta.get_field('status').choices]
        if new_status in valid_statuses:
            commande.status = new_status
            commande.save()
            messages.success(request, f"La commande #{commande.id} est maintenant '{commande.get_status_display()}'.")
    return redirect(request.META.get('HTTP_REFERER', 'toutes_commandes'))

@employe_required
def delete_commande(request, pk):
    """Admin action to delete an order."""
    if request.method == 'POST':
        commande = get_object_or_404(Commande, pk=pk)
        commande.delete()
        messages.success(request, f"La commande #{pk} a été supprimée.")
    return redirect('toutes_commandes')