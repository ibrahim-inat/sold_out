"""
SOLD-OUT — tests/notifications/test_notifications.py
"""

import pytest
from django.core import mail
from django.contrib.auth import get_user_model
from apps.cart.models import Cart, CartItem
from apps.events.models import Event, Category
from apps.orders.services import OrderService
from apps.notifications.models import EmailLog

User = get_user_model()


@pytest.fixture
def test_user(db):
    # Kullanıcı oluşturulduğunda signal ile mail gitmesi gerekir.
    user = User.objects.create_user(username="testuser", email="test@test.com", password="password")
    return user

@pytest.fixture
def event(db):
    category = Category.objects.create(name="Test Category", slug="test-category")
    return Event.objects.create(
        title="Test Event for Email",
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
class TestNotificationSystem:
    
    def test_welcome_email_sent_on_user_creation(self):
        # Outbox temizle (önceki testlerden kalanlar varsa)
        mail.outbox.clear()
        
        # Yeni kullanıcı yarat
        new_user = User.objects.create_user(username="newuser", email="new@user.com", password="pwd")
        
        # 1 email gönderilmiş olmalı
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        
        assert email.subject == "SOLD-OUT'a Hoş Geldin!"
        assert email.to == ["new@user.com"]
        assert "newuser" in email.body
        
        # EmailLog kaydı oluşturulmalı
        log = EmailLog.objects.get(to_email="new@user.com")
        assert log.template_name == "welcome"
        assert log.status == "SENT"

    def test_order_confirmation_email_sent_on_success(self, test_user, cart):
        mail.outbox.clear()
        
        billing_data = {"full_name": "Test Name", "email": "buyer@test.com", "phone": "123"}
        order = OrderService.create_order_from_cart(test_user, cart, billing_data)
        
        # Simüle başarılı ödeme
        payment_data = {"card_number": "4111 1111 1111 1234", "card_brand": "VISA"}
        OrderService.process_payment(order, payment_data)
        
        # 1 email (order confirmation) gitmeli
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        
        assert order.order_number in email.subject
        assert email.to == ["buyer@test.com"]
        
        # İçerikte etkinlik adı ve bilet kodları olmalı
        assert "Test Event for Email" in email.body
        
        # İlk bileti bulalım
        ticket = order.tickets.first()
        assert ticket.ticket_code in email.body
        
        # EmailLog kaydı
        log = EmailLog.objects.filter(to_email="buyer@test.com", template_name="order_confirmation").first()
        assert log is not None
        assert log.status == "SENT"

    def test_failed_payment_no_email(self, test_user, cart):
        mail.outbox.clear()
        
        billing_data = {"full_name": "Test Name", "email": "buyer@test.com", "phone": "123"}
        order = OrderService.create_order_from_cart(test_user, cart, billing_data)
        
        # Başarısız ödeme (0000 simülasyonu)
        payment_data = {"card_number": "4111 1111 1111 0000", "card_brand": "VISA"}
        OrderService.process_payment(order, payment_data)
        
        # Mail gitmemeli
        assert len(mail.outbox) == 0

    def test_email_log_creation_for_failed_smtp(self, monkeypatch):
        # SMTP gönderimini mock'layarak hata fırlatmasını sağla
        def mock_send(*args, **kwargs):
            raise Exception("SMTP Bağlantı Hatası")
            
        monkeypatch.setattr("django.core.mail.EmailMultiAlternatives.send", mock_send)
        
        from apps.notifications.services import EmailService
        
        # Senkron _send_sync çağırıyoruz test için
        log = EmailService._send_sync("welcome", {"username":"test"}, "fail@test.com", "Test Subject")
        
        assert log.status == "FAILED"
        assert "SMTP Bağlantı Hatası" in log.error_message
