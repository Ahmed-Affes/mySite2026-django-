"""
Authentication decorators for the magasin app.
"""
from functools import wraps
from django.shortcuts import redirect


def login_required(view_func):
    """Magasin-specific login decorator - always redirects to magasin login"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            path = request.get_full_path()
            return redirect(f'/magasin/login/?next={path}')
        return view_func(request, *args, **kwargs)
    return wrapper
