"""
SOLD-OUT — apps.core.views
"""

from django.views.generic import TemplateView

from apps.events.models import Category
from apps.events.views import get_featured_events, get_upcoming_events


class HomeView(TemplateView):
    """SOLD-OUT ana sayfası — gerçek etkinlik verileriyle."""

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_events"] = get_featured_events(limit=6)
        context["upcoming_events"] = get_upcoming_events(limit=8)
        context["categories"] = Category.objects.filter(is_active=True)
        return context
