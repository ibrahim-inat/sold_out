"""
SOLD-OUT — apps.events.models

Category: Etkinlik kategorileri.
Event:    Etkinlik bilgileri (quantity-bazlı kapasite modeli).
"""

from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Etkinlik kategorisi (Konser, Tiyatro, Spor vb.)."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Slug")
    icon = models.CharField(
        max_length=50, blank=True, verbose_name="İkon", help_text="Emoji veya ikon sınıfı"
    )
    description = models.TextField(blank=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    """Etkinlik modeli — quantity bazlı kapasite yönetimi."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Taslak"
        PUBLISHED = "PUBLISHED", "Yayında"
        SOLD_OUT = "SOLD_OUT", "Tükendi"
        CANCELLED = "CANCELLED", "İptal Edildi"
        COMPLETED = "COMPLETED", "Tamamlandı"

    title = models.CharField(max_length=200, verbose_name="Etkinlik Adı")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Açıklama")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Kategori",
    )
    organizer = models.ForeignKey(
        "users.Organizer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="Organizatör",
    )
    cover_image = models.ImageField(
        upload_to="events/covers/", blank=True, null=True, verbose_name="Kapak Görseli"
    )
    date = models.DateField(verbose_name="Tarih")
    time = models.TimeField(verbose_name="Saat")
    location = models.CharField(max_length=250, verbose_name="Mekan")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Fiyat (₺)"
    )
    capacity = models.PositiveIntegerField(default=100, verbose_name="Kapasite")
    tickets_sold = models.PositiveIntegerField(default=0, verbose_name="Satılan Bilet")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Durum",
    )
    is_featured = models.BooleanField(default=False, verbose_name="Öne Çıkan mı?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme")

    class Meta:
        verbose_name = "Etkinlik"
        verbose_name_plural = "Etkinlikler"
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return self.title

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def available_tickets(self) -> int:
        """Kalan bilet sayısı."""
        return max(0, self.capacity - self.tickets_sold)

    @property
    def is_past(self) -> bool:
        """Etkinlik tarihi geçmiş mi?"""
        return self.date < date.today()

    @property
    def is_sold_out(self) -> bool:
        """Kapasite dolduysa True döner."""
        return self.tickets_sold >= self.capacity

    @property
    def average_rating(self) -> float:
        """Etkinliğin ortalama puanını hesaplar (1-5 arası). Yorum yoksa 0.0 döner."""
        from django.db.models import Avg
        # Sadece onaylanmış yorumlar
        result = self.comments.filter(is_approved=True).aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else 0.0

    @property
    def comment_count(self) -> int:
        """Onaylanmış yorum sayısını döndürür."""
        return self.comments.filter(is_approved=True).count()

    def get_absolute_url(self) -> str:
        return reverse("events:detail", kwargs={"slug": self.slug})

    # ── Slug auto-generation ─────────────────────────────────────────────

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    # ── Validation ───────────────────────────────────────────────────────

    def clean(self):
        """DRAFT → PUBLISHED geçişinde tarih geçmişte olamaz."""
        super().clean()
        if self.status == self.Status.PUBLISHED and self.date and self.date < date.today():
            raise ValidationError(
                {"date": "Yayına alınacak etkinliğin tarihi geçmiş olamaz."}
            )
