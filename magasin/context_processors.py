from .models import Categorie


def categories(request):
    """Return all categories so the sidebar can render without each view repeating it."""
    return {'categories': Categorie.objects.all()}
