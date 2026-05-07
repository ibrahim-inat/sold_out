"""
SOLD-OUT — apps.payments.admin
"""

from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "card_brand", "card_last4", "status", "paid_at")
    list_filter = ("status", "card_brand", "paid_at")
    search_fields = ("order__order_number",)

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False
