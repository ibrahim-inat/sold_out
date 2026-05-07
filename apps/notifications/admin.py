"""
SOLD-OUT — apps.notifications.admin
"""

from django.contrib import admin
from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("to_email", "subject", "template_name", "status", "sent_at", "user")
    list_filter = ("status", "sent_at", "template_name")
    search_fields = ("to_email", "subject", "user__username")
    readonly_fields = ("user", "to_email", "subject", "template_name", "status", "error_message", "sent_at")

    def has_add_permission(self, request):
        # EmailLog'lar otomatik oluşturulur, manuel eklenemez
        return False

    def has_change_permission(self, request, obj=None):
        # Kayıtlar salt okunurdur
        return False

    def has_delete_permission(self, request, obj=None):
        # Silme izni verilebilir ancak genelde loglar saklanır
        return super().has_delete_permission(request, obj)
