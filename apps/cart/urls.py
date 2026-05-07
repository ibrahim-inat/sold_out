"""
SOLD-OUT — apps.cart.urls
"""

from django.urls import path

from .views import (
    AddToCartView,
    CartDetailView,
    ClearCartView,
    RemoveCartItemView,
    UpdateCartItemView,
)

app_name = "cart"

urlpatterns = [
    path("", CartDetailView.as_view(), name="detail"),
    path("ekle/", AddToCartView.as_view(), name="add"),
    path("guncelle/<int:item_id>/", UpdateCartItemView.as_view(), name="update"),
    path("sil/<int:item_id>/", RemoveCartItemView.as_view(), name="remove"),
    path("temizle/", ClearCartView.as_view(), name="clear"),
]
