"""
SOLD-OUT — apps.tickets.admin
"""

from django.contrib import admin
from django.utils import timezone
from .models import Ticket


@admin.action(description="Seçilenleri 'Kullanıldı' olarak işaretle")
def mark_as_used(modeladmin, request, queryset):
    queryset.update(is_used=True, used_at=timezone.now())


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_code", "event", "holder_name", "is_used", "used_at")
    list_filter = ("is_used", "event", "created_at")
    search_fields = ("ticket_code", "holder_name", "order__order_number")
    
    actions = [mark_as_used]
    
    readonly_fields = ("ticket_code", "order", "event", "created_at")

    def has_add_permission(self, request):
        return False
