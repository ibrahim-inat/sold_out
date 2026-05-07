"""
SOLD-OUT — apps.cart.services

Cart management services.
"""

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Cart, CartItem


class CartService:
    @classmethod
    def get_or_create_cart(cls, request) -> Cart:
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                is_active=True
            )
            return cart
        else:
            # Anonim kullanıcı
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                user__isnull=True,
                is_active=True
            )
            request.session['cart_id'] = cart.id
            return cart

    @classmethod
    def add_item(cls, request, event, quantity: int):
        cart = cls.get_or_create_cart(request)
        
        with transaction.atomic():
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                event=event,
                defaults={'quantity': 0}
            )
            
            new_quantity = item.quantity + quantity
            
            if event.available_tickets < new_quantity:
                raise ValidationError(
                    f"Bu etkinlik için yeterli bilet yok. Kalan: {event.available_tickets}"
                )
            
            if new_quantity > 10:
                raise ValidationError("Bir etkinlikten en fazla 10 bilet alabilirsiniz.")
                
            item.quantity = new_quantity
            item.save()
            return item

    @classmethod
    def update_item(cls, request, item_id: int, quantity: int):
        cart = cls.get_or_create_cart(request)
        
        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return None
            
        if quantity <= 0:
            item.delete()
            return None
            
        if quantity > 10:
            raise ValidationError("Bir etkinlikten en fazla 10 bilet alabilirsiniz.")
            
        if item.event.available_tickets < quantity:
            raise ValidationError(
                f"Bu etkinlik için yeterli bilet yok. Kalan: {item.event.available_tickets}"
            )
            
        item.quantity = quantity
        item.save()
        return item

    @classmethod
    def remove_item(cls, request, item_id: int):
        cart = cls.get_or_create_cart(request)
        CartItem.objects.filter(id=item_id, cart=cart).delete()

    @classmethod
    def clear(cls, request):
        cart = cls.get_or_create_cart(request)
        cart.items.all().delete()

    @classmethod
    def merge_session_cart_to_user(cls, user, request):
        """
        Login olduğunda çağrılır.
        Anonim sepeti, kullanıcının aktif sepeti ile birleştirir.
        """
        cart_id = request.session.get('cart_id')
        if not cart_id:
            return

        try:
            anon_cart = Cart.objects.get(id=cart_id, user__isnull=True, is_active=True)
        except Cart.DoesNotExist:
            return

        if not anon_cart.items.exists():
            anon_cart.delete()
            return

        user_cart, _ = Cart.objects.get_or_create(user=user, is_active=True)

        with transaction.atomic():
            for anon_item in anon_cart.items.all():
                try:
                    user_item = CartItem.objects.get(cart=user_cart, event=anon_item.event)
                    new_quantity = user_item.quantity + anon_item.quantity
                    # Capacity limit
                    max_available = anon_item.event.available_tickets
                    user_item.quantity = min(new_quantity, max_available, 10)
                    user_item.save()
                except CartItem.DoesNotExist:
                    anon_item.cart = user_cart
                    anon_item.save()
            
            # Anonim sepeti temizle ve sil
            anon_cart.delete()
