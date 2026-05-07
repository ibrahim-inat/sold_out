"""
SOLD-OUT — apps.payments.models
"""

from django.db import models
from apps.orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Bekliyor"
        SUCCESS = "SUCCESS", "Başarılı"
        FAILED = "FAILED", "Başarısız"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_method = models.CharField(max_length=50, default="CREDIT_CARD", verbose_name="Ödeme Yöntemi")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tutar")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Durum"
    )
    
    # PCI-DSS standartları gereği tam kart numarası veya CVV KAYDEDİLMİYOR.
    card_brand = models.CharField(max_length=20, verbose_name="Kart Markası")
    card_last4 = models.CharField(max_length=4, verbose_name="Son 4 Hane")
    
    transaction_id = models.CharField(max_length=36, blank=True, verbose_name="İşlem ID")
    failure_reason = models.CharField(max_length=255, blank=True, verbose_name="Başarısızlık Nedeni")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Ödeme Tarihi")

    class Meta:
        verbose_name = "Ödeme"
        verbose_name_plural = "Ödemeler"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ödeme {self.transaction_id or self.id} - {self.order.order_number}"
