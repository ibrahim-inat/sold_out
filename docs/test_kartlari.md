# 💳 SOLD-OUT — Test Kartları Simülasyonu

Proje, canlı bir Sanal POS entegrasyonu içermemektedir. Test ortamında, PCI-DSS kuralları gereği gerçek ödeme ağ geçidi yerine `apps/payments/validators.py` tabanlı özel bir Luhn Algoritması simülasyonu çalışmaktadır.

Sipariş ve Ödeme testlerinizde **yalnızca** aşağıdaki kartları kullanabilirsiniz:

## 1. BAŞARILI İŞLEM (SUCCESS)
- **Kart Numarası:** `4111 1111 1111 2234`
- **Kart Sahibinin Adı:** Adınız Soyadınız (İçinde sayı içermeyen geçerli bir metin)
- **Son Kullanma Tarihi:** Gelecekte bir tarih (Örn: `12 / 2030`)
- **CVV:** `123`
- **Sonuç:** Luhn algoritmasını geçer, ödeme başarılı sayılır, Bilet üretilir, Sipariş PAID statüsüne alınır.

## 2. BİRİKİM/BAKİYE YETERSİZ (FAILED)
- **Kart Numarası:** `4111 1111 1111 0000`
- **Kart Sahibinin Adı:** Ad Soyad
- **Son Kullanma Tarihi:** `12 / 2030`
- **CVV:** `123`
- **Sonuç:** Son 4 hanesi `0000` olduğu için ödeme sistemi otomatik olarak işlemi reddeder ve `Bakiye yetersiz` hatası verir. Bilet ÜRETİLMEZ.

## 3. KART REDDEDİLDİ (FAILED)
- **Kart Numarası:** `4111 1111 1111 1111`
- **Kart Sahibinin Adı:** Ad Soyad
- **Son Kullanma Tarihi:** `12 / 2030`
- **CVV:** `123`
- **Sonuç:** Son 4 hanesi `1111` olduğu için işlem reddedilir, Sipariş FAILED statüsünde kalır.

## 4. LUHN HATASI (FORM GEÇERSİZ)
- **Kart Numarası:** `1234 5678 1234 5678` (veya rastgele herhangi bir numara)
- **Sonuç:** Form seviyesinde doğrulama hatası alınır. İşlem `OrderService` aşamasına hiç gitmeden kullanıcıya hata mesajı iletilir.
