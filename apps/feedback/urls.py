"""
SOLD-OUT — apps.feedback.urls
"""

from django.urls import path
from .views import AddCommentView, DeleteCommentView, FeedbackView

app_name = "feedback"

urlpatterns = [
    path("yorum-ekle/<slug:event_slug>/", AddCommentView.as_view(), name="add-comment"),
    path("yorum-sil/<int:pk>/", DeleteCommentView.as_view(), name="delete-comment"),
    path("geri-bildirim/", FeedbackView.as_view(), name="feedback"),
]
