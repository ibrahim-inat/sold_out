"""
SOLD-OUT — apps.notifications.models
"""

from django.db import models
from django.conf import settings


class EmailLog(models.Model):
    class Status(models.TextChoices):
        SENT = "SENT", "Gönderildi"
        FAILED = "FAILED", "Başarısız"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="emails",
        verbose_name="Kullanıcı"
    )
    to_email = models.EmailField(verbose_name="Alıcı E-posta")
    subject = models.CharField(max_length=255, verbose_name="Konu")
    template_name = models.CharField(max_length=100, verbose_name="Şablon Adı")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SENT, verbose_name="Durum")
    error_message = models.TextField(blank=True, verbose_name="Hata Mesajı")
    
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Zamanı")

    class Meta:
        verbose_name = "E-posta Kaydı"
        verbose_name_plural = "E-posta Kayıtları"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"[{self.status}] {self.subject} -> {self.to_email}"
