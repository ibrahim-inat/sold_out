"""
SOLD-OUT — apps.users.models

Profile modeli: Django auth.User'a OneToOne ek bilgi.
Organizer modeli: Etkinlik düzenleyici profili.
Signal ile kullanıcı kaydı sırasında otomatik Profile oluşturulur.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Kullanıcı profilini genişleten ek bilgiler."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Kullanıcı",
    )
    full_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ad Soyad",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefon",
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Doğum Tarihi",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Şehir",
    )
    bio = models.TextField(
        blank=True,
        verbose_name="Hakkında",
    )
    profile_photo = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
        verbose_name="Profil Fotoğrafı",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme")

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profiller"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.username} — Profil"


class Organizer(models.Model):
    """Etkinlik düzenleyici profili — onaylanmış organizatörler etkinlik oluşturabilir."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizer",
        verbose_name="Kullanıcı",
    )
    organization_name = models.CharField(
        max_length=200,
        verbose_name="Kuruluş Adı",
    )
    about = models.TextField(
        blank=True,
        verbose_name="Hakkında",
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Onaylı mı?",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")

    class Meta:
        verbose_name = "Organizatör"
        verbose_name_plural = "Organizatörler"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.organization_name} ({'✓' if self.is_verified else '✗'})"


# ── Signals ──────────────────────────────────────────────────────────────────


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Yeni kullanıcı oluşturulduğunda Profile otomatik yarat ve hoşgeldin e-postası at."""
    if created:
        Profile.objects.create(user=instance)
        try:
            from apps.notifications.services import EmailService
            EmailService.send_welcome_email(instance)
        except Exception:
            pass


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Kullanıcı kaydedildiğinde Profile'ı da kaydet."""
    if hasattr(instance, "profile"):
        instance.profile.save()
