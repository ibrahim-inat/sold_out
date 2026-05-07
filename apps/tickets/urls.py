"""
SOLD-OUT — apps.tickets.urls
"""

from django.urls import path
from .views import MyTicketsView, TicketDetailView

app_name = "tickets"

urlpatterns = [
    path("biletlerim/", MyTicketsView.as_view(), name="list"),
    path("<str:ticket_code>/", TicketDetailView.as_view(), name="detail"),
]
