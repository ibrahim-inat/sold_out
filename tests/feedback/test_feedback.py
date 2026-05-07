"""
SOLD-OUT — tests/feedback/test_feedback.py
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.events.models import Event, Category
from apps.orders.models import Order, OrderItem
from apps.feedback.models import Comment, Feedback

User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", password="pwd")

@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="otheruser", password="pwd")

@pytest.fixture
def event(db):
    category = Category.objects.create(name="Test", slug="test")
    return Event.objects.create(
        title="Test Event",
        slug="test-event",
        description="desc",
        date="2027-10-10",
        time="20:00:00",
        location="Loc",
        price=100,
        capacity=100,
        category=category,
        status="PUBLISHED"
    )

@pytest.fixture
def paid_order(db, test_user, event):
    order = Order.objects.create(
        user=test_user,
        order_number="SO-12345",
        full_name="Test User",
        email="test@test.com",
        phone="123",
        total_price=100,
        status="PAID"
    )
    OrderItem.objects.create(
        order=order,
        event=event,
        quantity=1,
        unit_price=100,
        subtotal=100
    )
    return order


@pytest.mark.django_db
class TestFeedbackSystem:
    
    def test_comment_requires_ticket(self, client, other_user, event):
        # other_user'ın bileti yok
        client.force_login(other_user)
        url = reverse("feedback:add-comment", kwargs={"event_slug": event.slug})
        
        response = client.post(url, {"comment": "Harika!", "rating": 5})
        # Bilet sahibi olmadığı için engellenmeli (view redirect yapıyor)
        assert response.status_code == 302
        assert not Comment.objects.filter(user=other_user, event=event).exists()

    def test_comment_success_with_ticket(self, client, test_user, event, paid_order):
        # test_user'ın bileti (PAID) var
        client.force_login(test_user)
        url = reverse("feedback:add-comment", kwargs={"event_slug": event.slug})
        
        response = client.post(url, {"comment": "Mükemmel", "rating": 5})
        assert response.status_code == 302
        
        comment = Comment.objects.get(user=test_user, event=event)
        assert comment.rating == 5
        assert comment.comment == "Mükemmel"

    def test_comment_update_on_second_submit(self, client, test_user, event, paid_order):
        client.force_login(test_user)
        url = reverse("feedback:add-comment", kwargs={"event_slug": event.slug})
        
        # İlk yorum
        client.post(url, {"comment": "İyi", "rating": 4})
        
        # İkinci yorum
        client.post(url, {"comment": "Güncelledim", "rating": 3})
        
        # Sadece 1 yorum olmalı
        comments = Comment.objects.filter(user=test_user, event=event)
        assert comments.count() == 1
        assert comments.first().rating == 3
        assert comments.first().comment == "Güncelledim"

    def test_average_rating_calculation(self, test_user, other_user, event):
        # test_user -> 5, other_user -> 4 = avg 4.5
        Comment.objects.create(user=test_user, event=event, comment="5", rating=5)
        Comment.objects.create(user=other_user, event=event, comment="4", rating=4)
        
        assert event.average_rating == 4.5
        assert event.comment_count == 2

    def test_unapproved_comment_not_in_average(self, test_user, other_user, event):
        Comment.objects.create(user=test_user, event=event, comment="5", rating=5, is_approved=True)
        Comment.objects.create(user=other_user, event=event, comment="1", rating=1, is_approved=False) # Onaysız
        
        assert event.average_rating == 5.0
        assert event.comment_count == 1

    def test_feedback_submission(self, client, test_user):
        client.force_login(test_user)
        url = reverse("feedback:feedback")
        
        response = client.post(url, {
            "category": "BUG",
            "comment": "Şurada bir hata var",
            "rating": 4
        })
        
        assert response.status_code == 302
        feedback = Feedback.objects.first()
        assert feedback.user == test_user
        assert feedback.category == "BUG"
