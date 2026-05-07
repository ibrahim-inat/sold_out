"""
SOLD-OUT — apps.cart.views

Cart views for displaying and managing the shopping cart.
"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View

from apps.events.models import Event
from .services import CartService


class CartDetailView(TemplateView):
    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartService.get_or_create_cart(self.request)
        context["cart"] = cart
        return context


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        event_id = request.POST.get("event_id")
        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            quantity = 1

        event = get_object_or_404(Event, id=event_id)
        
        try:
            CartService.add_item(request, event, quantity)
            messages.success(request, f"{event.title} sepete eklendi.")
        except ValidationError as e:
            messages.error(request, str(e.message) if hasattr(e, 'message') else str(e))
            
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class UpdateCartItemView(View):
    def post(self, request, item_id, *args, **kwargs):
        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            messages.error(request, "Geçersiz miktar.")
            return redirect("cart:detail")

        try:
            CartService.update_item(request, item_id, quantity)
            messages.success(request, "Sepet güncellendi.")
        except ValidationError as e:
            messages.error(request, str(e.message) if hasattr(e, 'message') else str(e))

        return redirect("cart:detail")


class RemoveCartItemView(View):
    def post(self, request, item_id, *args, **kwargs):
        CartService.remove_item(request, item_id)
        messages.success(request, "Ürün sepetten çıkarıldı.")
        return redirect("cart:detail")


class ClearCartView(View):
    def post(self, request, *args, **kwargs):
        CartService.clear(request)
        messages.success(request, "Sepet temizlendi.")
        return redirect("cart:detail")
