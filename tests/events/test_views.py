"""
SOLD-OUT — tests/events/test_views.py

EventListView ve EventDetailView testleri. Faz 6 kabul kriterleri: 7+ test.
"""

from datetime import date, time, timedelta

import pytest
from django.test import Client
from django.urls import reverse

from apps.events.models import Category, Event


@pytest.fixture
def category(db):
    return Category.objects.create(name="Test Kategori", slug="test-kategori", icon="🎵")


@pytest.fixture
def published_event(db, category):
    return Event.objects.create(
        title="Yayında Etkinlik",
        description="Test etkinliği açıklaması.",
        category=category,
        date=date.today() + timedelta(days=10),
        time=time(20, 0),
        location="Test Mekan",
        city="İstanbul",
        price=250,
        capacity=500,
        tickets_sold=100,
        status=Event.Status.PUBLISHED,
    )


@pytest.fixture
def draft_event(db, category):
    return Event.objects.create(
        title="Taslak Etkinlik",
        description="Taslak açıklama.",
        category=category,
        date=date.today() + timedelta(days=15),
        time=time(20, 0),
        location="Mekan",
        city="Ankara",
        price=100,
        capacity=200,
        status=Event.Status.DRAFT,
    )


@pytest.fixture
def past_event(db, category):
    return Event.objects.create(
        title="Geçmiş Etkinlik",
        description="Geçmiş açıklama.",
        category=category,
        date=date.today() - timedelta(days=5),
        time=time(20, 0),
        location="Eski Mekan",
        city="İzmir",
        price=150,
        capacity=300,
        status=Event.Status.PUBLISHED,
    )


@pytest.mark.django_db
class TestEventListView:
    """EventListView testleri."""

    def test_list_page_loads(self, client: Client, published_event):
        """GET /etkinlikler/ 200 dönmeli."""
        response = client.get(reverse("events:list"))
        assert response.status_code == 200

    def test_list_shows_published_events(self, client: Client, published_event):
        """Liste PUBLISHED etkinlikleri göstermeli."""
        response = client.get(reverse("events:list"))
        assert published_event.title in response.content.decode()

    def test_list_hides_draft_events(self, client: Client, draft_event):
        """Liste DRAFT etkinlikleri göstermemeli."""
        response = client.get(reverse("events:list"))
        assert draft_event.title not in response.content.decode()

    def test_list_hides_past_events(self, client: Client, past_event):
        """Liste geçmiş tarihli etkinlikleri göstermemeli."""
        response = client.get(reverse("events:list"))
        assert past_event.title not in response.content.decode()

    def test_search_filter(self, client: Client, published_event, draft_event):
        """?q= parametresi sonuçları filtrelemeli."""
        response = client.get(reverse("events:list"), {"q": "Yayında"})
        content = response.content.decode()
        assert published_event.title in content
        assert draft_event.title not in content

    def test_category_filter_reduces_results(self, client: Client, published_event, category):
        """?category= parametresi sonuçları kategoriye göre filtrelemeli."""
        other_cat = Category.objects.create(name="Başka Kategori", slug="baska-kategori")
        Event.objects.create(
            title="Başka Kategori Etkinliği",
            description="Açıklama",
            category=other_cat,
            date=date.today() + timedelta(days=5),
            time=time(19, 0),
            location="Mekan",
            city="Bursa",
            price=100,
            capacity=100,
            status=Event.Status.PUBLISHED,
        )
        response = client.get(reverse("events:list"), {"category": category.slug})
        content = response.content.decode()
        assert published_event.title in content
        assert "Başka Kategori Etkinliği" not in content

    def test_city_filter(self, client: Client, published_event):
        """?city= parametresi şehre göre filtrelemeli."""
        response = client.get(reverse("events:list"), {"city": "İstanbul"})
        assert response.status_code == 200
        assert published_event.title in response.content.decode()

    def test_no_results_empty_state(self, client: Client):
        """Etkinlik yoksa boş durum göstermeli."""
        response = client.get(reverse("events:list"), {"q": "varolan-hicbir-etkinlik-zzz"})
        assert response.status_code == 200
        assert "bulunamadı" in response.content.decode()


@pytest.mark.django_db
class TestEventDetailView:
    """EventDetailView testleri."""

    def test_detail_page_loads(self, client: Client, published_event):
        """PUBLISHED etkinlik detay sayfası 200 dönmeli."""
        response = client.get(published_event.get_absolute_url())
        assert response.status_code == 200
        assert published_event.title in response.content.decode()

    def test_draft_event_returns_404(self, client: Client, draft_event):
        """DRAFT etkinlik 404 dönmeli."""
        response = client.get(draft_event.get_absolute_url())
        assert response.status_code == 404

    def test_detail_shows_price(self, client: Client, published_event):
        """Detay sayfasında fiyat gösterilmeli."""
        response = client.get(published_event.get_absolute_url())
        assert "250" in response.content.decode()

    def test_detail_shows_location(self, client: Client, published_event):
        """Detay sayfasında konum gösterilmeli."""
        response = client.get(published_event.get_absolute_url())
        assert published_event.location in response.content.decode()
