# 🚀 SOLD-OUT — Dağıtım (Deployment) Kılavuzu

Bu belge, SOLD-OUT projesinin bir üretim ortamında (Ubuntu 22.04 LTS) nasıl yayına alınacağını adım adım anlatır.

---

## 1. Sunucu Hazırlığı
Temel paketleri ve Python 3.12, PostgreSQL 16, Nginx gibi servisleri kurun:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.12 python3.12-venv python3.12-dev build-essential \
                 postgresql-16 postgresql-contrib nginx curl certbot python3-certbot-nginx -y
```

## 2. Veritabanı Kurulumu (PostgreSQL)

```bash
sudo -u postgres psql
```

Açılan SQL konsolunda:
```sql
CREATE DATABASE soldout_db;
CREATE USER soldout_user WITH PASSWORD 'Guclu_Bir_Sifre_123!';
ALTER ROLE soldout_user SET client_encoding TO 'utf8';
ALTER ROLE soldout_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE soldout_user SET timezone TO 'Europe/Istanbul';
GRANT ALL PRIVILEGES ON DATABASE soldout_db TO soldout_user;
\q
```

## 3. Proje Dosyaları ve Sanal Ortam

```bash
cd /var/www/
sudo git clone <repo_url> sold_out
sudo chown -R $USER:$USER sold_out
cd sold_out

python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/prod.txt
```

## 4. Ortam Değişkenleri (.env)

`/var/www/sold_out/.env` dosyasını oluşturun ve aşağıdaki değerleri kendi sisteminize göre doldurun:

```env
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=çok-gizli-rastgele-üretilmiş-bir-anahtar-değeri
ALLOWED_HOSTS=soldout.com,www.soldout.com

DB_NAME=soldout_db
DB_USER=soldout_user
DB_PASSWORD=Guclu_Bir_Sifre_123!
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=sizin.mail@gmail.com
EMAIL_HOST_PASSWORD=gmail_uygulama_sifresi
DEFAULT_FROM_EMAIL="SOLD-OUT <sizin.mail@gmail.com>"
```

### Gmail App Password Adımları:
1. Google hesabınızda oturum açın.
2. "Güvenlik" sekmesine gidin.
3. "2 Adımlı Doğrulama"yı etkinleştirin.
4. "Uygulama Şifreleri" kısmına gidip "Posta" ve "Diğer" seçerek bir şifre (16 harfli) oluşturun.
5. Bu şifreyi `.env` dosyasındaki `EMAIL_HOST_PASSWORD` alanına yapıştırın.

## 5. Uygulamayı Hazırlama (Migrate & Collectstatic)

```bash
# Veritabanı tablolarını oluşturur
python manage.py migrate

# Tailwind CSS derlenir
python manage.py tailwind build

# Statik dosyaları (css, js, images) toplar ve WhiteNoise için hazırlar
python manage.py collectstatic --noinput

# Yönetici hesabı oluşturun
python manage.py createsuperuser
```

## 6. Gunicorn Kurulumu (Systemd)

Gunicorn'u arka planda çalıştırmak için bir Systemd servis dosyası oluşturun:
`sudo nano /etc/systemd/system/gunicorn.service`

```ini
[Unit]
Description=gunicorn daemon for SOLD-OUT
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sold_out
Environment="PATH=/var/www/sold_out/venv/bin"
EnvironmentFile=/var/www/sold_out/.env
ExecStart=/var/www/sold_out/venv/bin/gunicorn \
          --config /var/www/sold_out/gunicorn.conf.py \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Servisi başlatın:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 7. Nginx Kurulumu (Reverse Proxy)

`sudo nano /etc/nginx/sites-available/soldout`

```nginx
server {
    listen 80;
    server_name soldout.com www.soldout.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    # WhiteNoise statik dosyaları sunuyor ancak yine de media dosyaları Nginx üzerinden sunulmalıdır.
    location /media/ {
        alias /var/www/sold_out/media/;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

Sembolik link oluşturup Nginx'i yeniden başlatın:
```bash
sudo ln -s /etc/nginx/sites-available/soldout /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 8. HTTPS (Certbot / Let's Encrypt)

```bash
sudo certbot --nginx -d soldout.com -d www.soldout.com
```

Bu işlem Nginx ayarlarınızı otomatik güncelleyecek ve HTTP trafiğini HTTPS'e yönlendirecektir (`SECURE_SSL_REDIRECT = True` ayarımız nedeniyle uygulamanız HTTPS olmadan çalışmayı zaten reddedecektir).

## 🎉 Tebrikler! Uygulamanız yayında!
