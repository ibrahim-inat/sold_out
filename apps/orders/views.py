"""
SOLD-OUT — apps.orders.views
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import FormView, ListView, DetailView, TemplateView
from django.views import View

from apps.cart.services import CartService
from apps.payments.forms import PaymentForm
from .models import Order
from .services import OrderService, OrderCreationError


class CheckoutView(LoginRequiredMixin, View):
    template_name = "orders/checkout.html"

    def get(self, request, *args, **kwargs):
        cart = CartService.get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Sepetiniz boş.")
            return redirect("cart:detail")

        payment_form = PaymentForm()
        
        # Kullanıcının profil bilgilerinden fatura verilerini dolduralım
        user = request.user
        initial_billing = {
            "full_name": user.profile.full_name if hasattr(user, 'profile') else user.get_full_name(),
            "email": user.email,
            "phone": user.profile.phone if hasattr(user, 'profile') else "",
        }

        return render(request, self.template_name, {
            "cart": cart,
            "payment_form": payment_form,
            "billing": initial_billing,
        })

    def post(self, request, *args, **kwargs):
        cart = CartService.get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Sepetiniz boş.")
            return redirect("cart:detail")

        # Fatura bilgileri formdan manuel alınıyor (Form class kullanmadık, basit dict)
        billing_data = {
            "full_name": request.POST.get("full_name"),
            "email": request.POST.get("email"),
            "phone": request.POST.get("phone"),
        }

        payment_form = PaymentForm(request.POST)
        
        if payment_form.is_valid():
            try:
                # Sipariş Oluştur
                order = OrderService.create_order_from_cart(request.user, cart, billing_data)
                
                # Ödemeyi İşle
                payment = OrderService.process_payment(order, payment_form.cleaned_data)
                
                if payment.status == "SUCCESS":
                    return redirect("orders:success", order_number=order.order_number)
                else:
                    return redirect("orders:failed", order_number=order.order_number)
                    
            except OrderCreationError as e:
                messages.error(request, str(e))
                return redirect("cart:detail")
        else:
            return render(request, self.template_name, {
                "cart": cart,
                "payment_form": payment_form,
                "billing": billing_data,
            })


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "orders/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = self.kwargs.get("order_number")
        context["order"] = get_object_or_404(Order, order_number=order_number, user=self.request.user)
        return context


class OrderFailedView(LoginRequiredMixin, TemplateView):
    template_name = "orders/failed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = self.kwargs.get("order_number")
        context["order"] = get_object_or_404(Order, order_number=order_number, user=self.request.user)
        return context


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/detail.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
