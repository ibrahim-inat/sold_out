"""
SOLD-OUT — apps.users.views

RegisterView    : Yeni kullanıcı kaydı
ProfileView     : Profil görüntüleme (login required)
ProfileUpdateView: Profil güncelleme (login required)
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ProfileForm, RegisterForm


class RegisterView(FormView):
    """Yeni kullanıcı kayıt sayfası."""

    template_name = "users/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("users:login")

    def dispatch(self, request, *args, **kwargs):
        # Zaten giriş yapmışsa ana sayfaya yönlendir
        if request.user.is_authenticated:
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Formu kontrol edin, bazı alanlar hatalı.",
        )
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Profil görüntüleme sayfası."""

    template_name = "users/profile.html"
    login_url = reverse_lazy("users:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.request.user.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, FormView):
    """Profil düzenleme sayfası."""

    template_name = "users/profile_edit.html"
    form_class = ProfileForm
    login_url = reverse_lazy("users:login")
    success_url = reverse_lazy("users:profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user.profile
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Profiliniz başarıyla güncellendi.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Formu kontrol edin.")
        return super().form_invalid(form)
