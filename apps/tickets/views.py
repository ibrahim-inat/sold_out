"""
SOLD-OUT — apps.tickets.views
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView, DetailView
from .models import Ticket


class MyTicketsView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/my_tickets.html"
    context_object_name = "tickets"

    def get_queryset(self):
        # Kullanıcıya ait tüm biletler
        qs = Ticket.objects.filter(order__user=self.request.user).select_related("event", "order")
        
        # Tab filtresi (upcoming / past)
        tab = self.request.GET.get("tab", "upcoming")
        now_date = timezone.now().date()
        
        if tab == "past":
            qs = qs.filter(event__date__lt=now_date).order_params() if hasattr(qs, "order_params") else qs.filter(event__date__lt=now_date).order_by("-event__date")
        else:
            qs = qs.filter(event__date__gte=now_date).order_by("event__date")
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_tab"] = self.request.GET.get("tab", "upcoming")
        return context


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = "tickets/detail.html"
    context_object_name = "ticket"
    slug_field = "ticket_code"
    slug_url_kwarg = "ticket_code"

    def get_queryset(self):
        # Sadece bilet sahibi görüntüleyebilir
        return Ticket.objects.filter(order__user=self.request.user).select_related("event")
