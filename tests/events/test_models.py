"""
SOLD-OUT — tests/events/test_models.py

Category ve Event model testleri.
"""

from datetime import date, timedelta, time

import pytest
from django.core.exceptions import ValidationError

from apps.events.models import Category, Event


@pytest.fixture
def category(db):
    """Test kategorisi oluştur."""
    return Category.objects.create(name="Konser", icon="🎵", description="Müzik etkinlikleri")


@pytest.fixture
def future_event(db, category):
    """Gelecek tarihli test etkinliği oluştur."""
    return Event.objects.create(
        title="Test Konseri",
        description="Test açıklama",
        category=category,
        date=date.today() + timedelta(days=30),
        time=time(20, 0),
        location="Test Mekan",
        city="İstanbul",
        price=250,
        capacity=1000,
        tickets_sold=300,
        status=Event.Status.PUBLISHED,
    )


@pytest.mark.django_db
class TestCategoryModel:
    """Category model testleri."""

    def test_category_str(self, category):
        """Category.__str__ kategori adını döndürmeli."""
        assert str(category) == "Konser"

    def test_category_slug_auto_generated(self, category):
        """Slug otomatik oluşturulmalı."""
        assert category.slug == "konser"

    def test_category_verbose_name(self):
        """verbose_name Türkçe olmalı."""
        assert Category._meta.verbose_name == "Kategori"
        assert Category._meta.verbose_name_plural == "Kategoriler"


@pytest.mark.django_db
class TestEventModel:
    """Event model testleri."""

    def test_event_str(self, future_event):
        """Event.__str__ başlığı döndürmeli."""
        assert str(future_event) == "Test Konseri"

    def test_slug_auto_generated(self, future_event):
        """Slug otomatik oluşturulmalı."""
        assert future_event.slug == "test-konseri"

    def test_slug_duplicate_suffix(self, category):
        """Aynı isimle ikinci etkinlik slug'a -1 eklemeli."""
        Event.objects.create(
            title="Tekrar Etkinlik",
            description="Açıklama 1",
            category=category,
            date=date.today() + timedelta(days=10),
            time=time(20, 0),
            location="Mekan",
            city="Ankara",
            price=100,
        )
        ev2 = Event.objects.create(
            title="Tekrar Etkinlik",
            description="Açıklama 2",
            category=category,
            date=date.today() + timedelta(days=20),
            time=time(21, 0),
            location="Mekan 2",
            city="İstanbul",
            price=150,
        )
        assert ev2.slug == "tekrar-etkinlik-1"

    def test_available_tickets(self, future_event):
        """available_tickets = capacity - tickets_sold."""
        assert future_event.available_tickets == 700

    def test_available_tickets_never_negative(self, future_event):
        """available_tickets asla negatif olmamalı."""
        future_event.tickets_sold = 1500  # capacity'den fazla
        assert future_event.available_tickets == 0

    def test_is_sold_out_false(self, future_event):
        """Bilet kaldıysa is_sold_out False olmalı."""
        assert future_event.is_sold_out is False

    def test_is_sold_out_true(self, future_event):
        """Bilet kalmadıysa is_sold_out True olmalı."""
        future_event.tickets_sold = 1000
        assert future_event.is_sold_out is True

    def test_is_past_false(self, future_event):
        """Gelecek tarihli etkinlik is_past False olmalı."""
        assert future_event.is_past is False

    def test_is_past_true(self, category):
        """Geçmiş tarihli etkinlik is_past True olmalı."""
        ev = Event.objects.create(
            title="Geçmiş Etkinlik",
            description="Eski",
            category=category,
            date=date.today() - timedelta(days=10),
            time=time(20, 0),
            location="Eski Mekan",
            city="İzmir",
            price=100,
            status=Event.Status.COMPLETED,
        )
        assert ev.is_past is True

    def test_get_absolute_url(self, future_event):
        """get_absolute_url doğru URL döndürmeli."""
        url = future_event.get_absolute_url()
        assert "/etkinlikler/" in url
        assert future_event.slug in url

    def test_clean_published_past_date(self, category):
        """PUBLISHED durumunda geçmiş tarih ValidationError vermeli."""
        ev = Event(
            title="Geçmiş Published",
            description="Hata",
            category=category,
            date=date.today() - timedelta(days=5),
            time=time(20, 0),
            location="Mekan",
            city="Bursa",
            price=100,
            status=Event.Status.PUBLISHED,
        )
        with pytest.raises(ValidationError) as exc_info:
            ev.clean()
        assert "date" in exc_info.value.message_dict

    def test_clean_draft_past_date_ok(self, category):
        """DRAFT durumunda geçmiş tarih kabul edilmeli."""
        ev = Event(
            title="Geçmiş Draft",
            description="OK",
            category=category,
            date=date.today() - timedelta(days=5),
            time=time(20, 0),
            location="Mekan",
            city="Bursa",
            price=100,
            status=Event.Status.DRAFT,
        )
        ev.clean()  # ValidationError fırlatmamalı

    def test_event_meta(self):
        """Event Meta verbose_name Türkçe olmalı."""
        assert Event._meta.verbose_name == "Etkinlik"
        assert Event._meta.verbose_name_plural == "Etkinlikler"
