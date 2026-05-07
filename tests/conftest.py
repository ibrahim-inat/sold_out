"""
SOLD-OUT — tests/conftest.py
"""

import pytest
from django.test import Client

from tests.factories import UserFactory, CategoryFactory, EventFactory, CartFactory, CartItemFactory


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def test_user(db):
    return UserFactory(username="testuser", email="test@test.com")


@pytest.fixture
def other_user(db):
    return UserFactory(username="otheruser", email="other@test.com")


@pytest.fixture
def authenticated_client(client, test_user):
    client.force_login(test_user)
    return client


@pytest.fixture
def published_event(db):
    category = CategoryFactory(name="Concert", slug="concert")
    return EventFactory(
        title="Epic Concert",
        slug="epic-concert",
        status="PUBLISHED",
        category=category,
        capacity=100,
        price="150.00"
    )


@pytest.fixture
def full_cart(db, test_user):
    cart = CartFactory(user=test_user, is_active=True)
    events = EventFactory.create_batch(3, status="PUBLISHED")
    for event in events:
        CartItemFactory(cart=cart, event=event, quantity=1)
    return cart
