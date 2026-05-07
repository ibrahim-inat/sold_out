"""
SOLD-OUT — Development settings.

Usage:
    DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py runserver
"""

from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = True

# Geçici geliştirme DB override'ı: PostgreSQL henüz hazır değilse SQLite'a düş.
# AGENTS.md hedefi PostgreSQL'dir; bu yalnızca lokal doğrulama için kullanılır.
if config("USE_SQLITE", default=False, cast=bool):
    DATABASES = {  # noqa: F811
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Django Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

# Email — console backend for development (prints emails to terminal)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
