# SOLD-OUT — Gemini / Anti-Gravity Specific Rules

> Bu dosya `AGENTS.md`'den **daha yüksek önceliğe** sahiptir.
> Anti-Gravity IDE'ye özel yönlendirmeler burada tanımlanır.

## Genel İlkeler
- Her fazın sonunda **deliverables** (çıktı listesi) ve **acceptance criteria** (kabul kriterleri) kontrol edilmelidir.
- Plan Mode ile başla; önce Plan Artifact üret, onay sonrası uygula.
- Tek seferde 1 faz tamamla. Bağımsız fazlar paralel çalıştırılabilir, bağımlı fazlar sıralı.

## Prompt Kuralları
- `@dosya` ve `@klasör` sentaksı ile bağlam ver.
- Her prompt **belirsizlik bırakmayan**, **kendi başına çalıştırılabilir** ve **doğrulanabilir çıktı** üretmelidir.
- Türkçe UI metinleri, İngilizce kod — bu kurala kesinlikle uy.

## Migration Güvenliği
- `makemigrations` öncesi model diff'i göster.
- Mevcut migration dosyalarını asla silme.
- `migrate` komutunu çalıştırmadan önce onay iste.

## Test Kuralları
- Her faz sonunda ilgili testleri çalıştır.
- Test raporunu artifact olarak üret.
- Kırılan testler varsa fazı tamamlanmış sayma.

## Dosya Organizasyonu
```
sold_out/
├── AGENTS.md
├── GEMINI.md
├── .env                    # Asla commit'leme
├── .gitignore
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/
│   ├── __init__.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── dev.py
│       └── prod.py
├── apps/
│   ├── accounts/           # Kullanıcı auth & profil
│   ├── events/             # Etkinlik CRUD
│   ├── tickets/            # Bilet & sipariş
│   └── payments/           # Ödeme simülasyonu
├── templates/
│   ├── base.html
│   ├── includes/
│   ├── accounts/
│   ├── events/
│   ├── tickets/
│   └── payments/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
└── tests/
    ├── conftest.py
    ├── accounts/
    ├── events/
    ├── tickets/
    └── payments/
```

## Yasaklar (MVP)
- QR kod, koltuk seçimi, social login, 2FA, SMS, gerçek banka, iade sistemi → YAPMA.
- Dış API çağrısı YAPMA.
- `DEBUG = True` sadece dev'de.
