"""
SOLD-OUT — tests/test_security.py
"""

import pytest
from django.urls import reverse
from django.test import Client

from apps.events.models import Event
from apps.orders.models import Order
from apps.cart.models import Cart
from tests.factories import OrderFactory


@pytest.mark.django_db
class TestSecurity:
    
    def test_csrf_token_required_for_post(self, client):
        """CSRF token olmayan POST 403 (veya Django default) dönüyor."""
        # Django'nun default test client'ı CSRF'yi atlar (EnforceCSRFChecks kapalıdır).
        # Bu yüzden client'i csrf_checks=True ile başlatalım
        csrf_client = Client(enforce_csrf_checks=True)
        
        login_url = reverse("users:login")
        # csrf middleware'i takılacak ve 403 dönecek
        response = csrf_client.post(login_url, {"username": "test", "password": "pwd"})
        assert response.status_code == 403

    def test_anonymous_user_redirected(self, client):
        """Anonim kullanıcı LoginRequiredMixin korunan view'larda redirect oluyor."""
        protected_urls = [
            reverse("users:profile"),
            reverse("orders:list"),
            reverse("tickets:list"),
        ]
        
        for url in protected_urls:
            response = client.get(url)
            assert response.status_code == 302
            assert "/hesap/giris/" in response.url

    def test_user_cannot_access_other_users_order(self, client, test_user, other_user):
        """User A'nın siparişine User B erişemiyor (404)."""
        # User A (test_user) için bir sipariş oluştur
        order = OrderFactory(user=test_user, status="PAID")
        
        # User B (other_user) ile giriş yap
        client.force_login(other_user)
        
        # Sipariş detayına erişmeye çalış
        detail_url = reverse("orders:detail", kwargs={"order_number": order.order_number})
        response = client.get(detail_url)
        
        # get_object_or_404(Order, order_number=..., user=request.user) olduğu için 404 dönmeli
        assert response.status_code == 404

    def test_sql_injection_protection(self, client, published_event):
        """SQL injection denemesi hata vermiyor, ORM nedeniyle güvenli."""
        events_url = reverse("events:list")
        
        # Tipik bir SQL injection payload'u
        payload = "' OR 1=1 --"
        response = client.get(f"{events_url}?q={payload}")
        
        # 500 hatası almamalı, 200 dönmeli ve boş/az sonuç göstermeli
        assert response.status_code == 200
        # ORM bunu string olarak arayacağı için hata fırlatmaz, güvenlidir.
