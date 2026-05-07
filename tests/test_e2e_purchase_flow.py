"""
SOLD-OUT — tests/test_e2e_purchase_flow.py
"""

import pytest
import datetime
from django.urls import reverse
from apps.tickets.models import Ticket
from apps.orders.models import Order
from apps.events.models import Event


@pytest.mark.django_db
class TestE2EPurchaseFlow:
    """
    Kullanıcının sisteme giriş yapıp bilet satın alma senaryosunu uçtan uca test eder.
    register -> login -> event listesi gör -> kategori filtresi uygula -> 
    event detayı aç -> sepete ekle (qty=2) -> sepeti gör -> checkout'a git -> 
    payment formu doldur (geçerli Luhn kart) -> SUCCESS sayfası -> 
    sipariş listesi -> bilet listesi (2 adet ticket görmeli).
    """
    
    def test_purchase_flow(self, client, test_user, published_event):
        # 1. Login
        # Kayıt işlemi zaten view ile test ediliyor, burada doğrudan login ile başlayalım
        login_url = reverse("users:login")
        response = client.post(login_url, {"username": test_user.username, "password": "testpassword123"})
        assert response.status_code == 302
        assert response.url == reverse("core:home")
        
        # 2. Event listesini gör
        events_url = reverse("events:list")
        response = client.get(events_url)
        assert response.status_code == 200
        assert published_event.title in response.content.decode("utf-8")
        
        # 3. Kategori filtresi uygula
        category_url = f"{events_url}?category={published_event.category.slug}"
        response = client.get(category_url)
        assert response.status_code == 200
        assert published_event.title in response.content.decode("utf-8")
        
        # 4. Event detayı aç
        detail_url = reverse("events:detail", kwargs={"slug": published_event.slug})
        response = client.get(detail_url)
        assert response.status_code == 200
        
        # 5. Sepete ekle (qty=2)
        add_to_cart_url = reverse("cart:add")
        response = client.post(add_to_cart_url, {"event_id": published_event.id, "quantity": 2})
        assert response.status_code == 302
        
        # 6. Sepeti gör
        cart_url = reverse("cart:detail")
        response = client.get(cart_url)
        assert response.status_code == 200
        html = response.content.decode("utf-8")
        assert published_event.title in html
        assert "value=\"2\"" in html or ">2<" in html
        
        # 7 & 8. Checkout formunu doldur ve Ödeme yap (tek aşama)
        checkout_url = reverse("orders:checkout")
        response = client.post(checkout_url, {
            "full_name": "E2E Test User",
            "email": "e2e@test.com",
            "phone": "5551234567",
            "card_number": "4111111111112234",
            "card_holder": "Eki Test User",
            "expiry_month": "12",
            "expiry_year": str(datetime.datetime.now().year + 2),
            "cvv": "123"
        })
        
        # Sipariş oluşturuldu ve ödeme başarılı, redirect olmalı
        if response.status_code == 200:
            print(response.context.get("payment_form").errors)
        assert response.status_code == 302
        
        # Siparişin oluşturulduğunu ve PAID olduğunu kontrol et
        order = Order.objects.filter(user=test_user).first()
        assert order is not None
        assert order.status == "PAID"
        assert response.url == reverse("orders:success", kwargs={"order_number": order.order_number})
        
        # 9. Sipariş listesi
        orders_url = reverse("orders:list")
        response = client.get(orders_url)
        assert response.status_code == 200
        assert order.order_number in response.content.decode("utf-8")
        
        # 10. Bilet listesi
        tickets_url = reverse("tickets:list")
        response = client.get(tickets_url)
        assert response.status_code == 200
        
        # 2 adet bilet görmeli
        tickets = Ticket.objects.filter(order=order)
        assert tickets.count() == 2
        
        html = response.content.decode("utf-8")
        for ticket in tickets:
            assert ticket.ticket_code in html
            
        # Etkinliğin satılan bilet sayısı güncellenmiş olmalı
        published_event.refresh_from_db()
        assert published_event.tickets_sold == 2
