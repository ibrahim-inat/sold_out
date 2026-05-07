--
description: Migration üret ve uygula (güvenli)
--
1. python manage.py makemigrations --dry-run --verbosity 2
2. Çıktıyı bana göster, ONAY iste.
3. Onay sonrası: python manage.py makemigrations
4. python manage.py migrate --plan
5. Tekrar onay iste, sonra: python manage.py migrate
