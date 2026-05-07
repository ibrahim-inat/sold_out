"""
SOLD-OUT — apps.tickets.models
"""

import secrets
from django.db import models
from django.conf import settings

from apps.orders.models import Order
from apps.events.models import Event


def generate_unique_ticket_code() -> str:
    """SOTK-XXXXXXXXXX formatında benzersiz bilet kodu üretir."""
    while True:
        code = f"SOTK-{secrets.token_hex(5).upper()}"
        if not Ticket.objects.filter(ticket_code=code).exists():
            return code


class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets", verbose_name="Sipariş")
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="tickets", verbose_name="Etkinlik")
    
    ticket_code = models.CharField(
        max_length=16, 
        unique=True, 
        default=generate_unique_ticket_code, 
        verbose_name="Bilet Kodu"
    )
    
    holder_name = models.CharField(max_length=150, verbose_name="Bilet Sahibi")
    
    is_used = models.BooleanField(default=False, verbose_name="Kullanıldı mı?")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Kullanım Tarihi")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")

    class Meta:
        verbose_name = "Bilet"
        verbose_name_plural = "Biletler"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Bilet {self.ticket_code} - {self.event.title}"
