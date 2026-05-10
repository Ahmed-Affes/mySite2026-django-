"""
Shared authentication utilities for app-specific login redirects
"""
from django.shortcuts import redirect
from functools import wraps

def get_app_from_request(request):
    """Determine which app the request is for based on the path"""
    path = request.get_full_path()
    if path.startswith('/reddrop/'):
        return 'reddrop'
    elif path.startswith('/magasin/'):
        return 'magasin'
    else:
        return 'magasin'  # default


def custom_login_required(view_func):
    """
    Custom decorator that redirects to the correct login page based on the app.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            app = get_app_from_request(request)
            path = request.get_full_path()
            if app == 'reddrop':
                return redirect(f'/reddrop/connexion/?next={path}')
            else:  # magasin
                return redirect(f'/magasin/login/?next={path}')
        return view_func(request, *args, **kwargs)
    return wrapper
