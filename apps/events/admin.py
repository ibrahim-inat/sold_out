"""
SOLD-OUT — apps.events.admin
"""

from django.contrib import admin
from .models import Category, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon")
    prepopulated_fields = {"slug": ("name",)}


@admin.action(description="Seçilenleri Yayınla")
def mark_as_published(modeladmin, request, queryset):
    queryset.update(status="PUBLISHED")

@admin.action(description="Seçilenleri İptal Et")
def mark_as_cancelled(modeladmin, request, queryset):
    queryset.update(status="CANCELLED")

@admin.action(description="Seçilenleri Öne Çıkar")
def mark_as_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title", "category", "date", "time", "city", 
        "price", "status", "tickets_sold", "capacity", "is_featured"
    )
    list_editable = ("status", "is_featured")
    list_filter = ("status", "category", "date", "city", "is_featured")
    search_fields = ("title", "city", "location", "organizer__organization_name")
    
    readonly_fields = ("tickets_sold", "slug_info")
    actions = [mark_as_published, mark_as_cancelled, mark_as_featured]
    
    fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("title", "slug_info", "category", "organizer", "description", "cover_image")
        }),
        ("Tarih & Konum", {
            "fields": ("date", "time", "location", "city")
        }),
        ("Bilet & Fiyat", {
            "fields": ("price", "capacity", "tickets_sold")
        }),
        ("Durum", {
            "fields": ("status", "is_featured")
        }),
    )

    def slug_info(self, obj):
        return obj.slug if obj.pk else "Otomatik üretilecektir."
    slug_info.short_description = "Slug"
