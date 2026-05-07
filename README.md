# 🎫 SOLD-OUT — Çevrimiçi Etkinlik Bilet Satış Platformu

**SOLD-OUT**, Malatya Turgut Özal Üniversitesi Bilgisayar Mühendisliği bölümü "Yazılım Mühendisliği" dersi kapsamında geliştirilmiş; modern, güvenli ve kullanıcı dostu bir çevrimiçi etkinlik bilet satış platformudur. Bu platform, etkinlik organizatörlerinin kendi etkinliklerini yayınlayabildikleri, kullanıcıların kategorilere göre filtreleme yaparak bilet satın alabildikleri uçtan uca simüle edilmiş bir e-ticaret uygulamasıdır.

**Tarih:** 27.03.2026

---

## 👥 Proje Ekibi

| İsim | Rol |
|------|-----|
| **Adar Yiğit Tekdemir** | Takım Kaptanı & Veritabanı Uzmanı |
| **İbrahim İnat** | Backend Geliştirici |
| **Muhammed Karadeniz** | Frontend Geliştirici |
| **Muhammet Karakobak** | Test Mühendisi |

**Danışman:** Dilber Çetintaş

---

## 🛠 Teknoloji Yığını (Tech Stack)

- **Backend:** Python 3.12+, Django 5.2 LTS
- **Veritabanı:** PostgreSQL 16
- **Frontend:** Django Templates + Tailwind CSS v4 (django-tailwind-cli üzerinden)
- **Kimlik Doğrulama:** Django built-in session-based auth
- **E-posta Bildirimleri:** Django SMTP backend (Gmail App Password entegrasyonu)
- **Test ve CI/CD:** pytest, pytest-django, factory_boy, pytest-cov, GitHub Actions
- **Dağıtım (Deployment):** Gunicorn, Nginx, Docker, WhiteNoise

---

## 📸 Ekran Görüntüleri

Projemiz modern arayüz standartlarına sadık kalınarak tasarlanmıştır. Canlı bot testinden bazı ekran kayıtlarını / görüntülerini aşağıda bulabilirsiniz:

| Ana Sayfa | Etkinlik Detayı |
|:---:|:---:|
| ![Ana Sayfa](https://via.placeholder.com/600x300?text=SOLD-OUT+Ana+Sayfa) | ![Etkinlik Detayı](https://via.placeholder.com/600x300?text=Etkinlik+Detay+ve+Yorumlar) |

| Sepet / Checkout | Admin Paneli |
|:---:|:---:|
| ![Sepet ve Checkout](https://via.placeholder.com/600x300?text=Sepet+ve+Odeme+Ekrani) | ![Admin Panel](https://via.placeholder.com/600x300?text=SOLD-OUT+Ozel+Admin+Paneli) |

*(Not: Geliştirme sürecindeki "Browser Bot" aracılığıyla alınan WebP kayıtlarına referans alınmıştır.)*

---

## 🚀 Kurulum (Geliştirme Ortamı)

**1. Depoyu klonlayın ve klasöre girin:**
```bash
git clone <repo-url>
cd sold_out
```

**2. Sanal Ortam oluşturup aktifleştirin:**
```bash
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

**3. Bağımlılıkları kurun:**
```bash
pip install -r requirements/dev.txt
```

**4. Hızlı Başlangıç Özeti:**
```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
createdb soldout_db  # veya manuel postgres shell'de
python manage.py migrate
python manage.py createsuperuser
python manage.py tailwind build
python manage.py runserver
```
[http://localhost:8000](http://localhost:8000) adresinden projeye erişebilirsiniz.

---

## 🧪 Testleri Çalıştırma ve Kapsam

Projemizde %88'lik yüksek bir test kapsama (coverage) oranı bulunmaktadır.

```bash
# Tüm testleri paralel çalıştır
pytest -n auto

# Kapsam (coverage) raporunu görmek için
pytest --cov=apps --cov-report=term-missing
```

---

## 💳 Ödeme Simülasyonu (Test Kartları)

Bu projede PCI-DSS uyumluluğu gözetilerek hassas kredi kartı verileri **saklanmamaktadır**. Ödeme sistemi bir simülasyon (mock) üzerinden çalışmaktadır.

Sipariş ekranında aşağıdaki test kartlarını kullanabilirsiniz:
- `4111 1111 1111 2234` → **BAŞARILI** (Geçerli Luhn algoritması onayı)
- `4111 1111 1111 0000` → **BAŞARISIZ** (Bakiye yetersiz hatası simülasyonu)
- `4111 1111 1111 1111` → **BAŞARISIZ** (Kart reddedildi hatası simülasyonu)

*Not: Hata almamak için Son Kullanma Tarihi alanına her zaman gelecekteki bir tarihi ve Geçerli bir CVV (`123` vb.) girmelisiniz.*

---

## 🛡️ Dağıtım (Deployment) ve Güvenlik

Üretim ortamı hazırlıkları `.github/workflows/ci.yml`, `Dockerfile` ve `docker-compose.yml` kullanılarak yapılmıştır.  
Detaylı kurulumlar için lütfen ilgili dokümanlara başvurun:
* [DEPLOYMENT.md](DEPLOYMENT.md) (Ubuntu sunucu, Nginx, Gunicorn ve SSL rehberi)
* [SECURITY.md](SECURITY.md) (Güvenlik özellikleri, HTTPS yönlendirmeleri ve korumalar)

---

## ⚠️ MVP Kapsam Dışı Bırakılanlar

Bu proje "Minimum Viable Product" (MVP) hedefleri doğrultusunda geliştirilmiştir. Aşağıdaki özellikler mevcut sürümde (v1) bilinçli olarak **kapsam dışı** bırakılmıştır:
- Biletler için QR kod üretme ve doğrulama sistemi
- Etkinlik mekanında koltuk seçimi (şu an sadece miktar tabanlı)
- Sosyal medya hesaplarıyla giriş (Google, Facebook Social Login)
- 2 Faktörlü Kimlik Doğrulama (2FA) / SMS onayları
- Gerçek banka / Sanal POS entegrasyonu (İşlemler simülasyondur)
- Kullanıcıların iptal / iade (refund) işlemlerini otomatik yapabilmesi (Admin üzerinden manuel)

---

## 🗺️ Roadmap (Gelecek Geliştirmeler)

- [ ] **v1.1:** Kullanıcıların bilet iade süreçlerini panelden talep edebilmesi.
- [ ] **v1.2:** Organizatör dashboard'u: Etkinlik sahiplerine kendi bilet satış istatistiklerini görebileceği özel analitik arayüzü.
- [ ] **v1.3:** Etkinlik mekanı oturma planı tasarımı (Koltuk seçerek satın alma).
- [ ] **v2.0:** Gerçek Stripe / iyzico API'leri ile Sanal POS entegrasyonunun sağlanması.

---
**SOLD-OUT** - *Sınırsız Eğlence, Tek Tıkla Biletiniz.*
