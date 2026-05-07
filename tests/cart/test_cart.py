"""
SOLD-OUT — tests/cart/test_cart.py
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.cart.models import Cart, CartItem
from apps.events.models import Event, Category

User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", email="test@test.com", password="password")


@pytest.fixture
def event(db):
    category = Category.objects.create(name="Test Category", slug="test-category")
    return Event.objects.create(
        title="Test Event",
        description="Test desc",
        date="2027-10-10",
        time="20:00:00",
        location="Test Loc",
        city="Istanbul",
        price=100.00,
        capacity=50,
        tickets_sold=0,
        category=category,
        status="PUBLISHED"
    )


@pytest.mark.django_db
class TestCartFlow:
    def test_anonymous_user_can_add_to_cart(self, client, event):
        url = reverse("cart:add")
        response = client.post(url, {"event_id": event.id, "quantity": 2}, HTTP_REFERER="/")
        assert response.status_code == 302
        
        # Anonim sepet oluşturuldu mu?
        carts = Cart.objects.filter(user__isnull=True)
        assert carts.count() == 1
        cart = carts.first()
        assert cart.session_key is not None
        assert cart.items.count() == 1
        assert cart.items.first().quantity == 2

    def test_authenticated_user_can_add_to_cart(self, client, test_user, event):
        client.force_login(test_user)
        url = reverse("cart:add")
        response = client.post(url, {"event_id": event.id, "quantity": 3}, HTTP_REFERER="/")
        assert response.status_code == 302
        
        cart = Cart.objects.get(user=test_user)
        assert cart.items.count() == 1
        assert cart.items.first().quantity == 3

    def test_merge_cart_on_login(self, client, test_user, event):
        # 1. Anonim olarak sepete ekle
        url = reverse("cart:add")
        client.post(url, {"event_id": event.id, "quantity": 2}, HTTP_REFERER="/")
        
        # 2. Login ol
        response = client.post(reverse("users:login"), {"username": "testuser", "password": "password"})
        assert response.status_code == 302

        
        # 3. User cart'a taşındı mı?
        cart = Cart.objects.get(user=test_user)
        assert cart.items.count() == 1
        assert cart.items.first().quantity == 2
        
        # Anonim sepet silindi mi?
        assert Cart.objects.filter(user__isnull=True).count() == 0

    def test_capacity_exceeded_shows_error(self, client, event):
        # Kapasite 50. 5 bilet kalması için 45 satılmış olmalı.
        event.tickets_sold = 45
        event.save()
        
        url = reverse("cart:add")
        response = client.post(url, {"event_id": event.id, "quantity": 6}, HTTP_REFERER="/", follow=True)
        
        # Mesajlarda hata olmalı
        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert "Bu etkinlik için yeterli bilet yok. Kalan: 5" in str(messages[0])
        
        # Sepete eklenmemiş olmalı
        assert CartItem.objects.count() == 0

    def test_max_10_tickets_per_event(self, client, event):
        url = reverse("cart:add")
        response = client.post(url, {"event_id": event.id, "quantity": 11}, HTTP_REFERER="/", follow=True)
        
        messages = list(response.context["messages"])
        assert "Bir etkinlikten en fazla 10 bilet alabilirsiniz." in str(messages[0])

    def test_update_item_quantity_to_zero_deletes_item(self, client, event):
        url = reverse("cart:add")
        client.post(url, {"event_id": event.id, "quantity": 2}, HTTP_REFERER="/")
        
        item = CartItem.objects.first()
        
        update_url = reverse("cart:update", args=[item.id])
        client.post(update_url, {"quantity": 0})
        
        assert CartItem.objects.count() == 0

    def test_remove_item_from_cart(self, client, event):
        client.post(reverse("cart:add"), {"event_id": event.id, "quantity": 2}, HTTP_REFERER="/")
        item = CartItem.objects.first()
        
        client.post(reverse("cart:remove", args=[item.id]))
        assert CartItem.objects.count() == 0

    def test_clear_cart(self, client, event):
        client.post(reverse("cart:add"), {"event_id": event.id, "quantity": 2}, HTTP_REFERER="/")
        assert CartItem.objects.count() == 1
        
        client.post(reverse("cart:clear"))
        assert CartItem.objects.count() == 0

    def test_navbar_context_processor(self, client, event):
        client.post(reverse("cart:add"), {"event_id": event.id, "quantity": 3}, HTTP_REFERER="/")
        response = client.get(reverse("events:list"))
        
        # Context processor çalışıyor mu?
        assert "cart_item_count" in response.context
        assert response.context["cart_item_count"] == 3
        assert response.context["cart_total"] == 300.00
