from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

EMPLOYE_GROUPS = {'Employé', 'Employee', 'groupeDSI', 'Employe'}


def is_admin(user):
    return user.is_authenticated and user.is_superuser


def is_employe(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.groups.filter(name__in=EMPLOYE_GROUPS).exists()


def is_client(user):
    return user.is_authenticated


def get_role_label(user):
    if not user.is_authenticated:
        return 'Invité'
    if user.is_superuser:
        return 'Administrateur'
    if user.is_staff or user.groups.filter(name__in=EMPLOYE_GROUPS).exists():
        return 'Employé'
    return 'Client'


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        raise PermissionDenied("Accès réservé aux administrateurs.")


class EmployeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return is_employe(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        raise PermissionDenied("Accès réservé aux employés et administrateurs.")


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            raise PermissionDenied("Accès réservé aux administrateurs.")
        return view_func(request, *args, **kwargs)
    return wrapper


def employe_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_employe(request.user):
            raise PermissionDenied("Accès réservé aux employés et administrateurs.")
        return view_func(request, *args, **kwargs)
    return wrapper


def role_context(request):
    user = request.user
    return {
        'user_role':       get_role_label(user),
        'is_admin_user':   is_admin(user),
        'is_employe_user': is_employe(user),
    }