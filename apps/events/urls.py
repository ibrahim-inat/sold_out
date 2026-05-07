"""
SOLD-OUT — apps.events.urls
"""

from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.EventListView.as_view(), name="list"),
    path("kategori/<slug:slug>/", views.EventListView.as_view(), name="by_category"),
    path("<slug:slug>/", views.EventDetailView.as_view(), name="detail"),
]
