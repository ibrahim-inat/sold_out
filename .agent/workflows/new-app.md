--
description: Yeni bir Django app'i AGENTS.md disiplinine uygun şekilde oluştur
--
1. apps/<app_name>/ klasörünü startapp ile oluştur.
2. apps.py'de name="apps.<app_name>" ayarla.
3. settings/base.py INSTALLED_APPS'e ekle.
4. urls.py iskeletini ve namespace'i hazırla, config/urls.py'a bağla.
5. tests/ alt klasörü ve __init__.py oluştur.
6. README.md'de "Apps" bölümüne yeni app'i ekle.
