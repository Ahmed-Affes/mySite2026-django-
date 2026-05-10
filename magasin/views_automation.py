@employe_required
@transaction.atomic
def bdc_auto_generate(request):
    """
    SMART AUTOMATION: Automatically generate BDCs for all products below stock_minimum.
    Groups products by supplier to minimize purchase orders.
    """
    low_stock_products = Produit.objects.filter(stock__lte=F('stock_minimum'), is_active=True).select_related('fournisseur')
    
    if not low_stock_products.exists():
        messages.info(request, "Tous les stocks sont à des niveaux optimaux. Aucune action requise.")
        return redirect('dashboard')

    # Group by supplier
    by_supplier = {}
    for p in low_stock_products:
        if p.fournisseur not in by_supplier:
            by_supplier[p.fournisseur] = []
        by_supplier[p.fournisseur].append(p)

    bdc_count = 0
    for supplier, products in by_supplier.items():
        # Create one BDC per supplier
        bdc = BonDeCommande.objects.create(
            fournisseur=supplier,
            cree_par=request.user,
            statut='brouillon',
            notes=f"Auto-généré suite à une alerte stock bas le {timezone.now().date()}."
        )
        for p in products:
            # Order enough to reach 2x stock_minimum + current deficit
            order_qty = (p.stock_minimum * 2)
            BonDeCommandeLigne.objects.create(
                bon=bdc,
                produit=p,
                quantite=order_qty,
                prix_achat=0 # To be filled by supplier/admin later
            )
        bdc_count += 1

    messages.success(request, f"Automatisation réussie : {bdc_count} Bon(s) de Commande ont été générés en brouillon pour réapprovisionner {low_stock_products.count()} produits.")
    return redirect('bdc_liste')
