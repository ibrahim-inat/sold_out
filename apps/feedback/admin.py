"""
SOLD-OUT — apps.feedback.admin
"""

from django.contrib import admin
from .models import Comment, Feedback


@admin.action(description="Seçilen yorumları onayla")
def approve_comments(modeladmin, request, queryset):
    queryset.update(is_approved=True)

@admin.action(description="Seçilen yorumların onayını kaldır")
def reject_comments(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at", "event")
    search_fields = ("user__username", "comment", "event__title")
    actions = [approve_comments, reject_comments]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("category", "user", "rating", "is_resolved", "created_at")
    list_filter = ("category", "is_resolved", "rating", "created_at")
    search_fields = ("user__username", "comment")
    list_editable = ("is_resolved",)
