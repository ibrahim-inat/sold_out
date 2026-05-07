"""
SOLD-OUT — apps.orders.models
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.events.models import Event


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Bekliyor"
        PAID = "PAID", "Ödendi"
        FAILED = "FAILED", "Başarısız"
        CANCELLED = "CANCELLED", "İptal Edildi"

    order_number = models.CharField(max_length=20, unique=True, verbose_name="Sipariş Numarası")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders", verbose_name="Kullanıcı"
    )
    
    # Fatura / İletişim Bilgileri
    full_name = models.CharField(max_length=150, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Tutar")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Durum"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Ödeme Tarihi")

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sipariş {self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(verbose_name="Adet")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ara Toplam")

    class Meta:
        verbose_name = "Sipariş Öğesi"
        verbose_name_plural = "Sipariş Öğeleri"

    def __str__(self):
        return f"{self.quantity} x {self.event.title} (Sipariş: {self.order.order_number})"
