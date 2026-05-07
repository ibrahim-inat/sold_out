"""
SOLD-OUT — apps.orders.urls
"""

from django.urls import path
from .views import (
    CheckoutView,
    OrderSuccessView,
    OrderFailedView,
    OrderListView,
    OrderDetailView,
)

app_name = "orders"

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("basarili/<str:order_number>/", OrderSuccessView.as_view(), name="success"),
    path("basarisiz/<str:order_number>/", OrderFailedView.as_view(), name="failed"),
    path("siparislerim/", OrderListView.as_view(), name="list"),
    path("<str:order_number>/", OrderDetailView.as_view(), name="detail"),
]
