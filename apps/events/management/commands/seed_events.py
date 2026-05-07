"""
SOLD-OUT — seed_events management komutu

8 kategori ve 30 örnek etkinlik oluşturur (geliştirme ortamı için).
"""

import random
from datetime import date, timedelta, time

from django.core.management.base import BaseCommand

from apps.events.models import Category, Event


CATEGORIES = [
    {"name": "Konser", "icon": "🎵", "description": "Müzik etkinlikleri ve konserler"},
    {"name": "Tiyatro", "icon": "🎭", "description": "Tiyatro oyunları ve gösteriler"},
    {"name": "Sinema", "icon": "🎬", "description": "Film gösterimleri ve festivaller"},
    {"name": "Stand-up", "icon": "🎤", "description": "Stand-up komedi gösterileri"},
    {"name": "Festival", "icon": "🎪", "description": "Müzik ve kültür festivalleri"},
    {"name": "Spor", "icon": "⚽", "description": "Spor müsabakaları ve etkinlikleri"},
    {"name": "Sergi", "icon": "🖼️", "description": "Sanat sergileri ve müze etkinlikleri"},
    {"name": "Workshop", "icon": "🎨", "description": "Atölye çalışmaları ve eğitimler"},
]

EVENTS_DATA = [
    # Konserler
    ("Tarkan Harbiye Konseri", "Konser", "Harbiye Cemil Topuzlu Açık Hava", "İstanbul", 850),
    ("Mor ve Ötesi Akustik Gece", "Konser", "IF Performance Hall", "İstanbul", 350),
    ("Duman Ankara Konseri", "Konser", "Congresium", "Ankara", 500),
    ("Ceza - Türk Rap Gecesi", "Konser", "Volkswagen Arena", "İstanbul", 400),
    ("Jazz Festivali Açılış Konseri", "Konser", "CRR Konser Salonu", "İstanbul", 250),
    # Tiyatro
    ("Hamlet — Modern Yorum", "Tiyatro", "Ankara Devlet Tiyatrosu", "Ankara", 180),
    ("Hisseli Harikalar Kumpanyası", "Tiyatro", "Harbiye Muhsin Ertuğrul Sahnesi", "İstanbul", 220),
    ("Küçük Prens Müzikali", "Tiyatro", "Zorlu PSM", "İstanbul", 300),
    ("Bir Delinin Hatıra Defteri", "Tiyatro", "İzmir Devlet Tiyatrosu", "İzmir", 150),
    # Sinema
    ("Nuri Bilge Ceylan Retrospektifi", "Sinema", "Atlas Sineması", "İstanbul", 80),
    ("Animasyon Film Festivali", "Sinema", "Cinemaximum", "Ankara", 60),
    ("Kısa Film Gecesi", "Sinema", "Kadıköy Sineması", "İstanbul", 45),
    # Stand-up
    ("Cem Yılmaz — Diamond Elite", "Stand-up", "Volkswagen Arena", "İstanbul", 600),
    ("Yılmaz Erdoğan Show", "Stand-up", "Jolly Joker", "İstanbul", 450),
    ("Genç Komedyenler Gecesi", "Stand-up", "BKM Mutfak", "İstanbul", 120),
    ("Stand-up Ankara", "Stand-up", "MEB Şura Salonu", "Ankara", 200),
    # Festival
    ("Cappadox Müzik Festivali", "Festival", "Kapadokya", "Nevşehir", 700),
    ("İstanbul Coffee Festival", "Festival", "KüçükÇiftlik Park", "İstanbul", 150),
    ("Zeytinli Rock Festivali", "Festival", "Zeytinli", "Balıkesir", 500),
    ("Gastronomi Festivali", "Festival", "Congresium", "Ankara", 100),
    # Spor
    ("Galatasaray — Fenerbahçe Derbisi", "Spor", "RAMS Park", "İstanbul", 800),
    ("Beşiktaş — Trabzonspor", "Spor", "Tüpraş Stadyumu", "İstanbul", 450),
    ("Euroleague Final Four", "Spor", "Sinan Erdem Spor Salonu", "İstanbul", 350),
    ("İstanbul Maratonu", "Spor", "Sultanahmet", "İstanbul", 50),
    # Sergi
    ("Ara Güler Fotoğraf Sergisi", "Sergi", "İstanbul Modern", "İstanbul", 120),
    ("Dijital Sanat Deneyimi", "Sergi", "Pera Müzesi", "İstanbul", 200),
    ("Anadolu Medeniyetleri", "Sergi", "Anadolu Medeniyetleri Müzesi", "Ankara", 90),
    # Workshop
    ("Fotoğrafçılık Atölyesi", "Workshop", "SALT Galata", "İstanbul", 250),
    ("Seramik Workshop", "Workshop", "Çankaya Sanat Evi", "Ankara", 180),
    ("Yaratıcı Yazarlık Atölyesi", "Workshop", "KüçükÇiftlik Park", "İstanbul", 150),
]

CITIES_CAPACITY = {
    "İstanbul": (500, 5000),
    "Ankara": (200, 2000),
    "İzmir": (200, 1500),
    "Nevşehir": (1000, 3000),
    "Balıkesir": (2000, 5000),
}


class Command(BaseCommand):
    help = "8 kategori ve 30 örnek etkinlik oluşturur."

    def handle(self, *args, **options):
        # Kategorileri oluştur
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "icon": cat_data["icon"],
                    "description": cat_data["description"],
                },
            )
            cat_map[cat.name] = cat
            status = "oluşturuldu" if created else "zaten var"
            self.stdout.write(f"  Kategori: {cat.name} — {status}")

        self.stdout.write(self.style.SUCCESS(f"\n[OK] {len(CATEGORIES)} kategori hazir."))

        # Etkinlikleri oluştur
        created_count = 0
        for i, (title, cat_name, location, city, price) in enumerate(EVENTS_DATA):
            if Event.objects.filter(title=title).exists():
                self.stdout.write(f"  Atlandı (zaten var): {title}")
                continue

            # Rastgele gelecek tarih (1-120 gün sonra)
            event_date = date.today() + timedelta(days=random.randint(7, 120))
            event_time = time(hour=random.choice([19, 20, 21]), minute=random.choice([0, 30]))

            # Kapasite
            cap_range = CITIES_CAPACITY.get(city, (200, 2000))
            capacity = random.randint(*cap_range)

            # Rastgele tickets_sold (0 — %70 kapasite arası)
            sold = random.randint(0, int(capacity * 0.7))

            event = Event(
                title=title,
                description=f"{title} etkinliğine hoş geldiniz! {location} mekanında "
                f"gerçekleşecek bu muhteşem etkinlikte yerinizi şimdiden ayırtın. "
                f"Sınırlı sayıda bilet mevcuttur.",
                category=cat_map[cat_name],
                date=event_date,
                time=event_time,
                location=location,
                city=city,
                price=price,
                capacity=capacity,
                tickets_sold=sold,
                status=Event.Status.PUBLISHED,
                is_featured=(i < 6),  # İlk 6 etkinlik öne çıkan
            )
            event.save()
            created_count += 1
            self.stdout.write(f"  [OK] {title} ({city})")

        self.stdout.write(
            self.style.SUCCESS(f"\n[OK] {created_count} etkinlik olusturuldu. Toplam: {Event.objects.count()}")
        )
