"""
SOLD-OUT — config.settings.prod
"""

from decouple import config, Csv
from .base import *

DEBUG = False

# Allowed hosts decouple config('ALLOWED_HOSTS', cast=Csv()) kullanarak
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# E-posta Konfigürasyonu (Gerçek SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# Güvenlik (Security Hardening)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 yıl
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# WhiteNoise statik dosya sunucusu ayarları
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
