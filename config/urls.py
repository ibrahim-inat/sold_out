"""
SOLD-OUT — URL Configuration.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

# Admin Site Özelleştirme
admin.site.site_header = "SOLD-OUT Yönetim Paneli"
admin.site.site_title = "SOLD-OUT Admin"
admin.site.index_title = "Hoşgeldin Admin 👋"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("hesap/", include("apps.users.urls")),
    path("etkinlikler/", include("apps.events.urls")),
    path("sepet/", include("apps.cart.urls")),
    path("siparisler/", include("apps.orders.urls")),
    path("odeme/", include("apps.payments.urls")),
    path("biletler/", include("apps.tickets.urls", namespace="tickets")),
    path("etkilesim/", include("apps.feedback.urls", namespace="feedback")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Django Debug Toolbar
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
