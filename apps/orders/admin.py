"""
SOLD-OUT — apps.orders.admin
"""

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    
    # Inline alanları da readonly yapalım
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.action(description="Seçilenleri ÖDENDİ (PAID) yap")
def mark_as_paid(modeladmin, request, queryset):
    queryset.update(status="PAID")

@admin.action(description="Seçilenleri İPTAL EDİLDİ (CANCELLED) yap")
def mark_as_cancelled(modeladmin, request, queryset):
    queryset.update(status="CANCELLED")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "user__username", "email", "full_name")
    
    inlines = [OrderItemInline]
    actions = [mark_as_paid, mark_as_cancelled]

    def get_readonly_fields(self, request, obj=None):
        # Admin formundaki bütün alanları readonly yapıyoruz, sadece action ile status değişebilir
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False
