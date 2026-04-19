from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path


class CustomUserCreationForm(UserCreationForm):
    """Applies Bootstrap form-control class to all fields automatically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


def login_redirect(request):
    """Redirect to the correct login page based on the URL"""
    if '/magasin/' in request.path:
        return redirect('login')
    elif '/reddrop/' in request.path:
        return redirect('blood_login')
    else:
        return redirect('login')


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Compte créé avec succès ! Vous pouvez maintenant vous connecter."
            )
            return redirect('login')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})


def home(request):
    return render(request,"home.html")