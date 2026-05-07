"""
SOLD-OUT — tests/factories.py
"""

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from apps.users.models import Profile, Organizer
from apps.events.models import Category, Event
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.tickets.models import Ticket
from apps.feedback.models import Comment, Feedback

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted if extracted else "testpassword123"
        self.set_password(password)


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    phone = factory.Faker("phone_number")
    city = factory.Faker("city")


class OrganizerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organizer

    user = factory.SubFactory(UserFactory)
    organization_name = factory.Faker("company")
    is_verified = True


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("word")
    slug = factory.Sequence(lambda n: f"category-{n}")
    icon = "🎸"


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Faker("catch_phrase")
    slug = factory.Sequence(lambda n: f"event-{n}")
    description = factory.Faker("text")
    date = factory.Faker("future_date")
    time = "20:00:00"
    location = factory.Faker("address")
    city = factory.Faker("city")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    capacity = 100
    tickets_sold = 0
    status = "PUBLISHED"
    category = factory.SubFactory(CategoryFactory)
    organizer = factory.SubFactory(OrganizerFactory)


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)
    is_active = True


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    event = factory.SubFactory(EventFactory)
    quantity = 1


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    order_number = factory.Sequence(lambda n: f"SO-TEST-{n}")
    full_name = factory.Faker("name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    total_price = Decimal("100.00")
    status = "PAID"


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    event = factory.SubFactory(EventFactory)
    quantity = 1
    unit_price = Decimal("100.00")
    subtotal = Decimal("100.00")


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    order = factory.SubFactory(OrderFactory)
    amount = Decimal("100.00")
    card_brand = "VISA"
    card_last4 = "1234"
    status = "SUCCESS"


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    order = factory.SubFactory(OrderFactory)
    event = factory.SubFactory(EventFactory)
    ticket_code = factory.Sequence(lambda n: f"TK-{n}")
    holder_name = factory.Faker("name")


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    comment = factory.Faker("text")
    rating = 5
    is_approved = True
