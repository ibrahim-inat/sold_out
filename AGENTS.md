# SOLD-OUT — Agent Operating Rules

## Tech Stack (kesin, değiştirme)
- Python 3.12, Django 5.x (LTS uygunsa 5.2), PostgreSQL 16
- Frontend: Django Templates + Tailwind CSS v4 (django-tailwind-cli paketi ile)
- Auth: Django built-in session-based auth (JWT YOK, allauth YOK, social login YOK)
- Admin: Django built-in admin (custom dashboard YOK)
- Email: Django SMTP backend (Gmail App Password)
- Test: pytest + pytest-django + factory_boy
- Bağımlılık yönetimi: pip + requirements/{base,dev,prod}.txt
- Ortam değişkenleri: python-decouple veya django-environ + .env

## Kod Kalitesi
- PEP 8 + black formatlama, line length 100
- Türkçe UI metinleri (label, button, mesaj), İngilizce kod (model adları, field, fonksiyon)
- Class-based view tercih et; sadece çok basit endpoint'lerde FBV kullan
- Her model __str__, Meta (verbose_name, ordering) tanımlamalı
- Settings dosyaları: config/settings/{base,dev,prod}.py şeklinde split
- Asla SECRET_KEY, EMAIL_HOST_PASSWORD, DB credential'ı koda gömme — sadece .env

## Güvenlik
- Tüm formlarda {% csrf_token %}
- ORM dışında raw SQL yazma
- DEBUG sadece dev ortamında True
- Şifre hash: Django default PBKDF2 (Argon2 opsiyonel)
- Üretim ortamı için ALLOWED_HOSTS, SECURE_SSL_REDIRECT, X-Frame-Options ayarları

## Safety Guardrails (agent kuralları)
- migrate veya makemigrations öncesi diff'i göster
- Mevcut migration dosyalarını silme; yeni migration üret
- pip freeze yapmadan önce sor; requirements dosyalarını manuel düzenle
- Veritabanı silme/drop komutları için MUTLAKA onay iste
- Dış API çağrısı YAPMA — ödeme gerçek banka entegrasyonu DEĞİL, simülasyondur

## Proje Bilgisi
- Proje adı: SOLD-OUT
- Üniversite: Malatya Turgut Özal Üniversitesi, Bilgisayar Mühendisliği
- Ekip: Adar Yiğit Tekdemir (Captain & DB), İbrahim İnat (Backend),
  Muhammed Karadeniz (Frontend), Muhammet Karakobak (Test)
- Danışman: Dilber Çetintaş

## MVP Kapsamı (UYGULAMA YASAKLARI)
- QR kod üretme YOK
- Koltuk seçimi YOK (yalnızca quantity modeli)
- Google/Facebook social login YOK
- 2FA YOK, SMS YOK, gerçek banka entegrasyonu YOK
- İade (refund) sistemi MVP'de YOK
