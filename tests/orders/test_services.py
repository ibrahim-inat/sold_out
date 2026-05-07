"""
SOLD-OUT — tests/orders/test_services.py
"""

import pytest
from apps.cart.models import Cart, CartItem
from apps.orders.services import OrderService, OrderCreationError
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.events.models import Event, Category
from django.contrib.auth import get_user_model

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

@pytest.fixture
def cart(db, test_user, event):
    cart = Cart.objects.create(user=test_user, is_active=True)
    CartItem.objects.create(cart=cart, event=event, quantity=2)
    return cart

@pytest.mark.django_db
class TestOrderServices:
    def test_create_order_from_cart(self, test_user, cart):
        billing_data = {"full_name": "Test User", "email": "test@test.com", "phone": "123456"}
        order = OrderService.create_order_from_cart(test_user, cart, billing_data)
        
        assert order.order_number.startswith("SO-")
        assert order.status == Order.Status.PENDING
        assert order.items.count() == 1
        assert order.total_price == 200.00
        
        # Cart temizlenmeli
        assert cart.items.count() == 0

    def test_capacity_exceeded_raises_error(self, test_user, cart, event):
        # 49 bilet satılmış, sepet 2 tane istiyor
        event.tickets_sold = 49
        event.save()
        
        billing_data = {"full_name": "Test User", "email": "test@test.com", "phone": "123456"}
        
        with pytest.raises(OrderCreationError):
            OrderService.create_order_from_cart(test_user, cart, billing_data)

    def test_process_payment_simulation_failed_0000(self, test_user, cart):
        order = OrderService.create_order_from_cart(test_user, cart, {})
        payment_data = {"card_number": "4111 1111 1111 0000", "card_brand": "VISA"}
        
        payment = OrderService.process_payment(order, payment_data)
        
        assert payment.status == Payment.Status.FAILED
        assert payment.failure_reason == "Bakiye yetersiz"
        
        order.refresh_from_db()
        assert order.status == Order.Status.FAILED

    def test_process_payment_simulation_failed_1111(self, test_user, cart):
        order = OrderService.create_order_from_cart(test_user, cart, {})
        payment_data = {"card_number": "4111 1111 1111 1111", "card_brand": "VISA"}
        
        payment = OrderService.process_payment(order, payment_data)
        
        assert payment.status == Payment.Status.FAILED
        assert payment.failure_reason == "Kart reddedildi"
        
        order.refresh_from_db()
        assert order.status == Order.Status.FAILED

    def test_process_payment_simulation_success(self, test_user, cart, event):
        order = OrderService.create_order_from_cart(test_user, cart, {})
        payment_data = {"card_number": "4111 1111 1111 1234", "card_brand": "VISA"}
        
        payment = OrderService.process_payment(order, payment_data)
        
        assert payment.status == Payment.Status.SUCCESS
        assert payment.card_last4 == "1234"
        assert payment.card_brand == "VISA"
        
        order.refresh_from_db()
        assert order.status == Order.Status.PAID
        
        event.refresh_from_db()
        assert event.tickets_sold == 2

    def test_order_and_payment_models_dont_store_full_card(self, test_user, cart):
        order = OrderService.create_order_from_cart(test_user, cart, {})
        payment_data = {"card_number": "4111 1111 1111 1234", "card_brand": "VISA"}
        payment = OrderService.process_payment(order, payment_data)
        
        # Sadece son 4 hane veritabanında var
        assert payment.card_last4 == "1234"
        # Tam kart numarası hiçbir attribute'da olmamalı
        assert not hasattr(payment, 'card_number')
