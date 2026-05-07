"""
SOLD-OUT — apps.users.signals

Kullanıcı sinyalleri.
"""

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from apps.cart.services import CartService


@receiver(user_logged_in)
def merge_cart_on_login(sender, user, request, **kwargs):
    """Kullanıcı giriş yaptığında anonim sepeti kullanıcı sepetiyle birleştirir."""
    CartService.merge_session_cart_to_user(user, request)
