"""
SOLD-OUT — tests/tickets/test_tickets.py
"""

import pytest
from django.urls import reverse
from apps.tickets.models import Ticket
from apps.orders.services import OrderService
from apps.cart.models import Cart, CartItem
from apps.events.models import Event, Category
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", email="test@test.com", password="password")

@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="otheruser", email="other@test.com", password="password")

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

@pytest.fixture
def cart(db, test_user, event):
    cart = Cart.objects.create(user=test_user, is_active=True)
    CartItem.objects.create(cart=cart, event=event, quantity=3)
    return cart


@pytest.mark.django_db
class TestTicketSystem:
    def test_successful_payment_creates_tickets(self, test_user, cart):
        billing_data = {"full_name": "Test User", "email": "test@test.com", "phone": "123"}
        order = OrderService.create_order_from_cart(test_user, cart, billing_data)
        
        # Simüle edilmiş başarılı ödeme
        payment_data = {"card_number": "4111 1111 1111 1234", "card_brand": "VISA"}
        payment = OrderService.process_payment(order, payment_data)
        
        # Payment başarılı mı?
        assert payment.status == "SUCCESS"
        
        # 3 adet bilet üretilmiş olmalı
        tickets = Ticket.objects.filter(order=order)
        assert tickets.count() == 3
        
        for ticket in tickets:
            assert ticket.ticket_code.startswith("SOTK-")
            assert len(ticket.ticket_code) == 15 # SOTK- (5) + 10 = 15 karakter. token_hex(5) = 10 karakter
            assert ticket.holder_name == "Test User"
            assert not ticket.is_used

    def test_failed_payment_does_not_create_tickets(self, test_user, cart):
        billing_data = {"full_name": "Test User", "email": "test@test.com", "phone": "123"}
        order = OrderService.create_order_from_cart(test_user, cart, billing_data)
        
        # Simüle edilmiş başarısız ödeme
        payment_data = {"card_number": "4111 1111 1111 0000", "card_brand": "VISA"}
        OrderService.process_payment(order, payment_data)
        
        tickets = Ticket.objects.filter(order=order)
        assert tickets.count() == 0

    def test_ticket_codes_are_unique(self, test_user, cart):
        billing_data = {"full_name": "Test User", "email": "test@test.com", "phone": "123"}
        order = OrderService.create_order_from_cart(test_user, cart, billing_data)
        payment_data = {"card_number": "4111 1111 1111 1234", "card_brand": "VISA"}
        OrderService.process_payment(order, payment_data)
        
        tickets = Ticket.objects.filter(order=order)
        codes = [t.ticket_code for t in tickets]
        
        # Set listesi uzunluğu aynı olmalı (Eşsizlik)
        assert len(codes) == len(set(codes))

    def test_my_tickets_view(self, client, test_user, cart):
        # Setup biletler
        billing_data = {"full_name": "Test User", "email": "test@test.com", "phone": "123"}
        order = OrderService.create_order_from_cart(test_user, cart, billing_data)
        payment_data = {"card_number": "4111 1111 1111 1234", "card_brand": "VISA"}
        OrderService.process_payment(order, payment_data)
        
        client.force_login(test_user)
        response = client.get(reverse("tickets:list"))
        
        assert response.status_code == 200
        # Context'te 3 bilet olmalı
        assert len(response.context["tickets"]) == 3

    def test_cannot_access_others_ticket(self, client, test_user, other_user, cart):
        billing_data = {"full_name": "Test User", "email": "test@test.com", "phone": "123"}
        order = OrderService.create_order_from_cart(test_user, cart, billing_data)
        payment_data = {"card_number": "4111 1111 1111 1234", "card_brand": "VISA"}
        OrderService.process_payment(order, payment_data)
        
        ticket = Ticket.objects.filter(order=order).first()
        
        # Diğer kullanıcı ile giriş yap
        client.force_login(other_user)
        url = reverse("tickets:detail", kwargs={"ticket_code": ticket.ticket_code})
        response = client.get(url)
        
        # Başkasının biletine erişim engellenmeli
        assert response.status_code == 404
