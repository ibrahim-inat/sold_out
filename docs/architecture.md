# 🏗️ SOLD-OUT — Mimari Tasarım (Architecture)

## MVT (Model-View-Template) Akışı
SOLD-OUT, standart Django MVT mimarisine göre yapılandırılmıştır:
- **Model**: Uygulamanın veritabanı (PostgreSQL) üzerindeki tablo tanımları ve veri doğrulama iş mantıkları (`models.py`, `services.py`).
- **View**: Gelen HTTP isteklerini karşılayan, uygun modeli sorgulayıp/değiştiren ve sonucu ilgili Template'e ileten iş kuralları. Class-Based Views (CBV) kullanılmıştır.
- **Template**: Son kullanıcıya HTML/Tailwind CSS formatında dönüş yapılan sunucu-taraflı render bileşeni.

## Uygulamalar (Apps) ve Bağımlılıkları
Proje, mikro hizmetlere yakın bir modüler yapıda bölünmüştür:
1. `users`: Tüm kimlik doğrulama, Profile ve Organizer modelleri.
2. `events`: Category ve Event (Etkinlik) modelleri. (Bağımlılık: `users.Organizer`)
3. `cart`: Kullanıcının mevcut sepeti. (Bağımlılık: `events.Event`)
4. `orders`: Kullanıcının sepetini satın alıma dönüştürdüğü sipariş. (Bağımlılık: `cart`, `events`, `users`)
5. `payments`: Luhn algoritması bazlı sanal POS simülatörü. (Bağımlılık: `orders`)
6. `tickets`: Ödemesi tamamlanan siparişlerden üretilen benzersiz biletler. (Bağımlılık: `orders`, `events`)
7. `notifications`: E-posta SMTP bildirimi işleri. (Bağımlılık: `orders`, `users`)
8. `feedback`: Etkinlik yorumları. (Bağımlılık: `users`, `events`, `orders` - sadece satın alanlar yorum yapabilir)

## Request Yaşam Döngüsü (Örnek: Sipariş Süreci)
1. Kullanıcı `CheckoutView` sayfasına post isteği atar (`apps/orders/views.py`).
2. View, kullanıcının sepetini `CartService` üzerinden çeker.
3. Form geçerliyse `OrderService.create_order_from_cart()` çağrılır (Kapasite kontrolü).
4. `OrderService.process_payment()` ile simüle ödeme yapılır (`apps/payments/validators.py`).
5. Ödeme başarılıysa `Ticket` modelleri oluşturulur ve kapasite düşülür.
6. `EmailService` arka planda SMTP ile bilet gönderir.
7. Kullanıcı `OrderSuccessView` sayfasına yönlendirilir.
