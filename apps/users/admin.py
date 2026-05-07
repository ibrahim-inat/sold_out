"""
SOLD-OUT — apps.users.admin
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User

from .models import Profile, Organizer


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profil Bilgileri"
    fk_name = "user"


class OrganizerInline(admin.StackedInline):
    model = Organizer
    can_delete = False
    verbose_name_plural = "Organizatör Bilgileri"
    fk_name = "user"


class CustomUserAdmin(DefaultUserAdmin):
    inlines = (ProfileInline, OrganizerInline)
    list_display = ("email", "username", "is_staff", "is_active", "date_joined")
    search_fields = ("email", "username")
    list_filter = ("is_staff", "is_active", "date_joined")
    ordering = ("-date_joined",)


# Unregister default User model and register the new one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
