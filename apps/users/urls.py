"""
SOLD-OUT — apps.users.urls
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import CustomLoginForm
from . import views

app_name = "users"

urlpatterns = [
    # Kayıt
    path("kayit/", views.RegisterView.as_view(), name="register"),
    # Giriş / Çıkış (Django built-in + custom form)
    path(
        "giris/",
        auth_views.LoginView.as_view(
            template_name="users/login.html",
            authentication_form=CustomLoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "cikis/",
        auth_views.LogoutView.as_view(next_page="core:home"),
        name="logout",
    ),
    # Profil
    path("profil/", views.ProfileView.as_view(), name="profile"),
    path("profil/duzenle/", views.ProfileUpdateView.as_view(), name="profile-edit"),
    # Şifre değiştirme
    path(
        "sifre-degistir/",
        auth_views.PasswordChangeView.as_view(
            template_name="users/password_change.html",
            success_url="/hesap/sifre-degistir/tamam/",
        ),
        name="password-change",
    ),
    path(
        "sifre-degistir/tamam/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html",
        ),
        name="password-change-done",
    ),
    # Şifre sıfırlama
    path(
        "sifre-sifirla/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.txt",
            html_email_template_name="users/password_reset_email.html",
            subject_template_name="users/password_reset_subject.txt",
            success_url="/hesap/sifre-sifirla/gonderildi/",
        ),
        name="password-reset",
    ),
    path(
        "sifre-sifirla/gonderildi/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html",
        ),
        name="password-reset-done",
    ),
    path(
        "sifre-sifirla/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/hesap/sifre-sifirla/tamamlandi/",
        ),
        name="password-reset-confirm",
    ),
    path(
        "sifre-sifirla/tamamlandi/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password-reset-complete",
    ),
]
