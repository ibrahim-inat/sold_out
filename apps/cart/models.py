"""
SOLD-OUT — apps.cart.models

Cart and CartItem models for database-backed shopping cart.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from apps.events.models import Event


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts"
    )
    session_key = models.CharField(max_length=64, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sepet"
        verbose_name_plural = "Sepetler"
        ordering = ["-created_at"]

    def clean(self):
        super().clean()
        if not self.user and not self.session_key:
            raise ValidationError("Sepet ya bir kullanıcıya ya da bir oturuma ait olmalıdır.")

    def __str__(self):
        if self.user:
            return f"Sepet ({self.user.username}) - {'Aktif' if self.is_active else 'Pasif'}"
        return f"Sepet (Anonim) - {'Aktif' if self.is_active else 'Pasif'}"

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sepet Öğesi"
        verbose_name_plural = "Sepet Öğeleri"
        unique_together = ("cart", "event")
        ordering = ["added_at"]

    def __str__(self):
        return f"{self.quantity} x {self.event.title}"

    @property
    def subtotal(self):
        return self.quantity * self.event.price
