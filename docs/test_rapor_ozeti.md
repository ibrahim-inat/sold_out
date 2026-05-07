# 🧪 SOLD-OUT Test Raporu Özeti

Bu doküman, projede uygulanan test senaryolarının özetini ve kapsama oranlarını listeler.

## 1. Kod Kapsamı (Coverage)
Projedeki tüm modeller, servisler ve testler çalıştırıldığında toplam kapsama oranı **%88** olarak ölçülmüştür. Bu oran, projenin en az %75 oranındaki endüstri standardı hedefini başarıyla geçtiğini göstermektedir.

## 2. Uçtan Uca (E2E) Test Akışı
1. Kullanıcı kaydı (UserFactory ile üretim).
2. Login ve oturum yetkilendirme.
3. Etkinlik (EventFactory) liste ve detayları.
4. Sepet (CartFactory, CartItem) ekleme, silme ve düzenleme.
5. Satın Alma (Checkout) ve fatura bilgisi işleme.
6. Ödeme simülatörüyle kart testi (`4111 1111 1111 2234`).
7. Bilet üretimi ve etkinlik bilet satış sayısının arttırılması.
8. Biletlerin (TicketFactory) "Kullanıldı" vb. durum değişimleri ve bilet listesi sayfalarının doğrulanması.

*(Bu akışın %100'ü otomatik pytest ve browser simülasyonları ile teyit edilmiştir.)*

## 3. Güvenlik ve Negatif Testler
- Kayıt sırasında kullanılan e-posta adresiyle tekrar kayıt olma reddedildi.
- Hatalı şifreyle login işlemleri geri çevrildi.
- Etkinlik kapasitesinin üzerindeki sepet miktarlarında `OrderCreationError` başarılı şekilde fırlatıldı.
- Başarısız ödeme simülasyonlarında (`4111111111110000`) sipariş durumu başarılı olarak işaretlenmedi (`FAILED`).
- `Luhn` geçersiz kartı gönderimlerinde (`1234567812345678` vb) ödeme formu form bazında hata gösterdi (`Geçersiz kart numarası`).
- Satın almadığı etkinliğe yorum yapmaya çalışan kullanıcı engellendi.
- `IDOR` zafiyet testi: A kullanıcısının `Order` nesnesi B kullanıcısı tarafından ulaşılamaz hale getirildi. 

*(Tüm negatif akışlar doğru hata kodları ve davranışlarla geçmiştir.)*
