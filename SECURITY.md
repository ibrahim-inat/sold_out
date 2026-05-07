# 🛡️ SOLD-OUT — Güvenlik Raporu ve Sertifikasyonu

Bu doküman, SOLD-OUT projesinde aktif olan güvenlik önlemlerini ve mimari yapının üretim ortamındaki (production) güvenlik standartlarını belgelemek için oluşturulmuştur.

---

## 1. Django Güvenlik Ayarları (Security Hardening)
`config/settings/prod.py` içerisinde aşağıdaki standart güvenlik yapılandırmaları aktiftir:

* **`DEBUG = False`**: Hata mesajları gizlenmiş ve `ALLOWED_HOSTS` denetimi zorunlu kılınmıştır.
* **`SECURE_SSL_REDIRECT = True`**: Tüm HTTP trafiği zorunlu olarak HTTPS'e yönlendirilir.
* **HTTP Strict Transport Security (HSTS)**: 1 yıllık (`31536000` saniye) HSTS politikası alt domainleri kapsayacak ve ön yüklemeye (preload) izin verecek şekilde aktiftir.
* **Çerez Güvenliği**: `SESSION_COOKIE_SECURE` ve `CSRF_COOKIE_SECURE` aktiftir. Tarayıcılar bu çerezleri sadece güvenli (HTTPS) bağlantılar üzerinden iletir.
* **İçerik Sniffing Koruması**: `SECURE_CONTENT_TYPE_NOSNIFF = True` ile MIME tabanlı saldırılar engellenmiştir.
* **Clickjacking Koruması**: `X_FRAME_OPTIONS = "DENY"` ile uygulamanın başka bir site içerisinde `<iframe` ile açılması tamamen yasaklanmıştır.
* **Browser XSS Filtresi**: `SECURE_BROWSER_XSS_FILTER = True` aktiftir.

## 2. Kimlik Doğrulama ve Yetkilendirme
* **Parola Hashleme**: Django'nun varsayılan güçlü parola özetleme algoritması `PBKDF2-SHA256` kullanılmaktadır.
* **Yetki Kontrolleri**: Satın alım yapan kullanıcının, siparişe kendi yetkisi dahilinde ulaşıp ulaşmadığı sıkı şekilde kontrol edilir (IDOR koruması `get_object_or_404(Order, user=request.user)` şeklinde uygulanır).

## 3. Finansal Veri ve Kredi Kartı (PCI-DSS Uyumluluk Notu)
* **KART BİLGİLERİ KAYDEDİLMEZ**: Uygulama mimarisinde kredi kartı numarası, CVV veya Son Kullanma Tarihi hiçbir koşulda veritabanında saklanmaz, loglara yazılmaz ve tarayıcıda önbelleklenmez (Otomatik tamamlama engellemeleri aktif edilmiştir).
* **Simülasyon Uyarı**: SOLD-OUT projesi akademik ve eğitim amaçlı bir MVP'dir. Kredi kartı işlemleri **Gerçek bir ödeme ağ geçidine (Payment Gateway / Sanal POS) bağlı değildir**. İşlemler sahte (mock) `PaymentService` üzerinden işlenir, geçişler "Luhn" algoritmasına dayalı simüle edilmiştir.

## 4. ORM ve SQL Enjeksiyon Koruması
* Tüm veritabanı işlemleri `Django ORM` üzerinden yapılarak otomatik parametreleştirme sağlanmaktadır. Hiçbir yerde ham (Raw) SQL kullanılmamıştır.
* SQL Injection (`' OR 1=1 --` vb.) payload'ları test ortamında taranmış ve zafiyet barındırmadığı teyit edilmiştir.

## 5. Raporlama ve İletişim
Projede olası bir güvenlik açığı tespit ederseniz, lütfen konuyu herkese açık (public) issue olarak açmak yerine doğrudan proje yetkililerine e-posta yoluyla iletiniz:
**İletişim:** `security@soldout.com` (Simülasyon adresi)
