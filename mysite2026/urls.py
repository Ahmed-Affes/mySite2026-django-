from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from .views import  home, register
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', register, name='register'),
    path('admin/',   admin.site.urls),

    path('magasin/login/', auth_views.LoginView.as_view(
            template_name='magasin/login.html',
            next_page='index'
         ), name='login'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='magasin/password_reset.html',
        email_template_name='magasin/password_reset_email.html',
        subject_template_name='magasin/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='magasin/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='magasin/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='magasin/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    path('magasin/', include('magasin.urls')),
    path('reddrop/', include('reddrop.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    if getattr(settings, 'STATICFILES_DIRS', None):
        urlpatterns += static(settings.STATIC_URL,
                              document_root=settings.STATICFILES_DIRS[0])