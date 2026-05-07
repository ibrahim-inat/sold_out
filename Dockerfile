FROM python:3.12-slim

# System bağımlılıklarını kur
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinimleri kopyala ve kur
COPY requirements/base.txt requirements/prod.txt ./requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Proje dosyalarını kopyala
COPY . .

# Statik dosyaları topla (Tailwind build + collectstatic)
RUN python manage.py tailwind build
RUN python manage.py collectstatic --noinput

# Gunicorn ile çalıştır
CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]
