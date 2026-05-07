"""
SOLD-OUT — apps.events.views
"""

from datetime import date

from django.db.models import Q
from django.http import Http404
from django.views.generic import DetailView, ListView

from .models import Category, Event


class EventListView(ListView):
    """Etkinlik listesi — arama, filtre ve sayfalama destekli."""

    model = Event
    template_name = "events/list.html"
    context_object_name = "events"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Event.objects.filter(status=Event.Status.PUBLISHED, date__gte=date.today())
            .select_related("category", "organizer")
            .order_by("date")
        )
        params = self.request.GET

        # Metin arama
        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(location__icontains=q)
                | Q(city__icontains=q)
            )

        # Kategori filtresi
        category_slug = params.get("category", "").strip()
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # Şehir filtresi
        city = params.get("city", "").strip()
        if city:
            qs = qs.filter(city__iexact=city)

        # Tarih aralığı
        date_from = params.get("date_from", "").strip()
        date_to = params.get("date_to", "").strip()
        if date_from:
            try:
                qs = qs.filter(date__gte=date_from)
            except Exception:
                pass
        if date_to:
            try:
                qs = qs.filter(date__lte=date_to)
            except Exception:
                pass

        # Sıralama
        sort = params.get("sort", "date_asc")
        sort_map = {
            "date_asc": "date",
            "date_desc": "-date",
            "price_asc": "price",
            "price_desc": "-price",
        }
        qs = qs.order_by(sort_map.get(sort, "date"))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["cities"] = (
            Event.objects.filter(status=Event.Status.PUBLISHED, date__gte=date.today())
            .values_list("city", flat=True)
            .distinct()
            .order_by("city")
        )
        context["current_params"] = self.request.GET
        context["q"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_city"] = self.request.GET.get("city", "")
        context["selected_sort"] = self.request.GET.get("sort", "date_asc")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        return context


class EventDetailView(DetailView):
    """Etkinlik detay sayfası — sadece PUBLISHED etkinlikler."""

    model = Event
    template_name = "events/detail.html"
    context_object_name = "event"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.status != Event.Status.PUBLISHED:
            raise Http404("Etkinlik bulunamadı.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        
        # Check if user has bought a ticket for this event
        user_has_ticket = False
        if self.request.user.is_authenticated:
            from apps.orders.models import Order
            user_has_ticket = Order.objects.filter(
                user=self.request.user, 
                status="PAID", 
                items__event=event
            ).exists()
        context["user_has_ticket"] = user_has_ticket

        # İlgili etkinlikler: Aynı kategori, kendisi hariç, yayında, en yakın 4 tane
        context["related_events"] = (
            Event.objects.filter(category=event.category, status="PUBLISHED")
            .exclude(pk=event.pk)
            .order_by("date", "time")[:4]
        )
        return context


def get_featured_events(limit=6):
    """Öne çıkan etkinlikleri döndürür — HomeView context helper."""
    return (
        Event.objects.filter(
            status=Event.Status.PUBLISHED,
            is_featured=True,
            date__gte=date.today(),
        )
        .select_related("category")
        .order_by("date")[:limit]
    )


def get_upcoming_events(limit=8):
    """Yaklaşan etkinlikler — HomeView context helper."""
    return (
        Event.objects.filter(status=Event.Status.PUBLISHED, date__gte=date.today())
        .select_related("category")
        .order_by("date")[:limit]
    )
