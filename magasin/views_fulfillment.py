@employe_required
@transaction.atomic
def commande_generer_bdc(request, pk):
    """
    SMART FULFILLMENT: Automatically generate BDCs from a client order.
    Groups order lines by supplier and creates a PO for each one.
    """
    commande = get_object_or_404(Commande, pk=pk)
    lignes = commande.lignes.all().select_related('produit__fournisseur')
    
    if not lignes.exists():
        messages.error(request, "Cette commande ne contient aucun article.")
        return redirect('commande_detail', pk=pk)

    # Check if BDCs already exist
    if BonDeCommande.objects.filter(commande=commande).exists():
        messages.warning(request, "Des bons de commande existent déjà pour cette commande.")
        return redirect('commande_detail', pk=pk)

    # Group items by supplier
    by_supplier = {}
    for ligne in lignes:
        supplier = ligne.produit.fournisseur
        if supplier not in by_supplier:
            by_supplier[supplier] = []
        by_supplier[supplier].append(ligne)

    bdc_count = 0
    for supplier, order_lines in by_supplier.items():
        # Create BDC for this supplier
        bdc = BonDeCommande.objects.create(
            fournisseur=supplier,
            commande=commande,
            cree_par=request.user,
            statut='brouillon',
            notes=f"Généré automatiquement pour la commande client #{commande.id}."
        )
        for line in order_lines:
            BonDeCommandeLigne.objects.create(
                bon=bdc,
                produit=line.produit,
                quantite=line.quantite,
                prix_achat=0 # Snapshot or manual entry
            )
        bdc_count += 1

    messages.success(request, f"Succès : {bdc_count} Bon(s) de commande ont été générés pour satisfaire cette commande.")
    return redirect('commande_detail', pk=pk)
