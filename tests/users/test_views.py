"""
SOLD-OUT — tests/users/test_views.py

Auth view testleri: Register, Login, Logout, Profile, ProfileUpdate,
PasswordChange, PasswordReset akışları. Faz 4 kabul kriterleri: 8+ test.
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestRegisterView:
    """Kayıt view testleri."""

    def test_register_page_loads(self, client: Client):
        """GET /hesap/kayit/ 200 dönmeli."""
        response = client.get(reverse("users:register"))
        assert response.status_code == 200
        assert "Hesap Oluştur" in response.content.decode()

    def test_register_success(self, client: Client):
        """Başarılı kayıt, giriş sayfasına yönlendirmeli."""
        response = client.post(
            reverse("users:register"),
            {
                "username": "viewtest",
                "email": "view@test.com",
                "password1": "GucluSifre123!",
                "password2": "GucluSifre123!",
            },
        )
        assert response.status_code == 302
        assert reverse("users:login") in response.url
        assert User.objects.filter(username="viewtest").exists()

    def test_register_duplicate_email(self, client: Client):
        """Zaten kayıtlı email ile kayıt hata vermeli."""
        User.objects.create_user(
            username="mevcut", email="existing@test.com", password="Test1234!"
        )
        response = client.post(
            reverse("users:register"),
            {
                "username": "yeni",
                "email": "existing@test.com",
                "password1": "GucluSifre123!",
                "password2": "GucluSifre123!",
            },
        )
        assert response.status_code == 200  # Form hatası, redirect yok

    def test_register_invalid_shows_errors(self, client: Client):
        """Geçersiz form ile sayfa tekrar yüklenmeli (200)."""
        response = client.post(
            reverse("users:register"),
            {"username": "", "email": "", "password1": "a", "password2": "b"},
        )
        assert response.status_code == 200

    def test_authenticated_user_redirected(self, client: Client):
        """Giriş yapmış kullanıcı kayıt sayfasına giremez."""
        User.objects.create_user(username="already", password="Test1234!")
        client.login(username="already", password="Test1234!")
        response = client.get(reverse("users:register"))
        assert response.status_code == 302


@pytest.mark.django_db
class TestLoginView:
    """Giriş view testleri."""

    def test_login_page_loads(self, client: Client):
        """GET /hesap/giris/ 200 dönmeli."""
        response = client.get(reverse("users:login"))
        assert response.status_code == 200

    def test_login_with_username(self, client: Client):
        """Username ile giriş başarılı olmalı."""
        User.objects.create_user(
            username="logintest", email="lt@test.com", password="Test1234!"
        )
        response = client.post(
            reverse("users:login"),
            {"username": "logintest", "password": "Test1234!"},
        )
        assert response.status_code == 302

    def test_login_with_email(self, client: Client):
        """Email ile giriş başarılı olmalı (EmailBackend)."""
        User.objects.create_user(
            username="emaillogin", email="email@test.com", password="Test1234!"
        )
        response = client.post(
            reverse("users:login"),
            {"username": "email@test.com", "password": "Test1234!"},
        )
        assert response.status_code == 302

    def test_login_wrong_password(self, client: Client):
        """Yanlış şifre ile giriş başarısız olmalı — 200 döner."""
        User.objects.create_user(username="faillogin", password="Test1234!")
        response = client.post(
            reverse("users:login"),
            {"username": "faillogin", "password": "YanlisSifre"},
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestLogoutView:
    """Çıkış view testleri."""

    def test_logout_redirects_to_home(self, client: Client):
        """POST /hesap/cikis/ ana sayfaya yönlendirmeli."""
        User.objects.create_user(username="logouttest", password="Test1234!")
        client.login(username="logouttest", password="Test1234!")
        response = client.post(reverse("users:logout"))
        assert response.status_code == 302
        assert response.url == "/"


@pytest.mark.django_db
class TestProfileView:
    """Profil view testleri."""

    def test_requires_login(self, client: Client):
        """Giriş yapmamış kullanıcı login'e yönlendirilmeli."""
        response = client.get(reverse("users:profile"))
        assert response.status_code == 302
        assert "giris" in response.url

    def test_profile_loads_for_authenticated(self, client: Client):
        """Giriş yapmış kullanıcı için profil 200 dönmeli."""
        User.objects.create_user(username="profview", password="Test1234!")
        client.login(username="profview", password="Test1234!")
        response = client.get(reverse("users:profile"))
        assert response.status_code == 200
        assert "profview" in response.content.decode()


@pytest.mark.django_db
class TestProfileUpdateView:
    """Profil düzenleme view testleri."""

    def test_requires_login(self, client: Client):
        """Giriş yapmamış kullanıcı login'e yönlendirilmeli."""
        response = client.get(reverse("users:profile-edit"))
        assert response.status_code == 302

    def test_edit_page_loads(self, client: Client):
        """Giriş yapmış kullanıcı düzenleme sayfasını görmeli."""
        User.objects.create_user(username="editview", password="Test1234!")
        client.login(username="editview", password="Test1234!")
        response = client.get(reverse("users:profile-edit"))
        assert response.status_code == 200

    def test_update_profile(self, client: Client):
        """Profil güncelleme başarılı olmalı."""
        user = User.objects.create_user(username="updateview", password="Test1234!")
        client.login(username="updateview", password="Test1234!")
        response = client.post(
            reverse("users:profile-edit"),
            {
                "full_name": "Test Kullanıcı",
                "phone": "+90 555 000 0000",
                "birth_date": "1995-06-15",
                "city": "Malatya",
                "bio": "Merhaba!",
            },
        )
        assert response.status_code == 302
        user.profile.refresh_from_db()
        assert user.profile.full_name == "Test Kullanıcı"
        assert user.profile.city == "Malatya"


@pytest.mark.django_db
class TestPasswordChangeView:
    """Şifre değiştirme view testleri."""

    def test_requires_login(self, client: Client):
        """Giriş yapmamış kullanıcı yönlendirilmeli."""
        response = client.get(reverse("users:password-change"))
        assert response.status_code == 302

    def test_page_loads_for_authenticated(self, client: Client):
        """Giriş yapmış kullanıcı şifre değiştirme sayfasını görmeli."""
        User.objects.create_user(username="chgtest", password="Test1234!")
        client.login(username="chgtest", password="Test1234!")
        response = client.get(reverse("users:password-change"))
        assert response.status_code == 200

    def test_password_change_success(self, client: Client):
        """Doğru şifre ile değiştirme işlemi yönlendirmeli."""
        User.objects.create_user(username="chgsuccess", password="OldPass123!")
        client.login(username="chgsuccess", password="OldPass123!")
        response = client.post(
            reverse("users:password-change"),
            {
                "old_password": "OldPass123!",
                "new_password1": "NewPass456!",
                "new_password2": "NewPass456!",
            },
        )
        assert response.status_code == 302

    def test_password_change_wrong_old(self, client: Client):
        """Yanlış mevcut şifre ile değiştirme başarısız olmalı."""
        User.objects.create_user(username="chgwrong", password="OldPass123!")
        client.login(username="chgwrong", password="OldPass123!")
        response = client.post(
            reverse("users:password-change"),
            {
                "old_password": "YanlisMevcut!",
                "new_password1": "NewPass456!",
                "new_password2": "NewPass456!",
            },
        )
        assert response.status_code == 200  # Hata — redirect yok


@pytest.mark.django_db
class TestPasswordResetView:
    """Şifre sıfırlama view testleri."""

    def test_reset_page_loads(self, client: Client):
        """GET /hesap/sifre-sifirla/ 200 dönmeli."""
        response = client.get(reverse("users:password-reset"))
        assert response.status_code == 200

    def test_reset_with_valid_email(self, client: Client):
        """Geçerli email ile şifre sıfırlama isteği yönlendirmeli."""
        User.objects.create_user(
            username="resetuser", email="reset@test.com", password="Test1234!"
        )
        response = client.post(
            reverse("users:password-reset"),
            {"email": "reset@test.com"},
        )
        assert response.status_code == 302

    def test_reset_with_invalid_email(self, client: Client):
        """Kayıtlı olmayan email ile de yönlendirmeli (güvenlik: email enumeration engelle)."""
        response = client.post(
            reverse("users:password-reset"),
            {"email": "yok@test.com"},
        )
        assert response.status_code == 302
