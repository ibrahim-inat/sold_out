"""
SOLD-OUT — apps.cart.context_processors
"""

from .services import CartService


def cart_summary(request):
    """Navbar'da badge ve toplam tutarı göstermek için context processor."""
    # Sadece request varsa işlem yap
    if not request:
        return {}

    cart = CartService.get_or_create_cart(request)
    
    return {
        "cart_item_count": cart.total_quantity,
        "cart_total": cart.total_price,
    }
