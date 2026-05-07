"""
SOLD-OUT — apps.feedback.models
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.events.models import Event


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments", verbose_name="Kullanıcı")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments", verbose_name="Etkinlik")
    
    comment = models.TextField(max_length=1000, verbose_name="Yorum")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Puan"
    )
    
    is_approved = models.BooleanField(default=True, verbose_name="Onaylı mı?")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")

    class Meta:
        verbose_name = "Etkinlik Yorumu"
        verbose_name_plural = "Etkinlik Yorumları"
        unique_together = ("user", "event") # Bir kullanıcı bir etkinliğe tek yorum atabilir
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.event.title} ({self.rating} Yıldız)"


class Feedback(models.Model):
    class Category(models.TextChoices):
        BUG = "BUG", "Hata / Bug"
        SUGGESTION = "SUGGESTION", "Öneri"
        OTHER = "OTHER", "Diğer"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="feedbacks", verbose_name="Kullanıcı")
    
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER, verbose_name="Kategori")
    comment = models.TextField(verbose_name="Geri Bildirim")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name="Genel Puan"
    )
    
    is_resolved = models.BooleanField(default=False, verbose_name="Çözüldü mü?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")

    class Meta:
        verbose_name = "Geri Bildirim"
        verbose_name_plural = "Geri Bildirimler"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.category} - {self.user.username if self.user else 'Anonim'}"
