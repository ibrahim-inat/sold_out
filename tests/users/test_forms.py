"""
SOLD-OUT — tests/users/test_forms.py

RegisterForm, CustomLoginForm ve ProfileForm testleri.
"""

import pytest
from django.contrib.auth.models import User

from apps.users.forms import CustomLoginForm, ProfileForm, RegisterForm


@pytest.mark.django_db
class TestRegisterForm:
    """RegisterForm testleri."""

    def test_valid_data(self):
        """Geçerli veri ile form valid olmalı."""
        form = RegisterForm(
            data={
                "username": "yenikullanici",
                "email": "yeni@test.com",
                "password1": "GucluSifre123!",
                "password2": "GucluSifre123!",
            }
        )
        assert form.is_valid(), form.errors

    def test_duplicate_email(self):
        """Aynı email ile kayıt hata vermeli."""
        User.objects.create_user(
            username="mevcut", email="tekrar@test.com", password="Test1234!"
        )
        form = RegisterForm(
            data={
                "username": "yeniuser",
                "email": "tekrar@test.com",
                "password1": "GucluSifre123!",
                "password2": "GucluSifre123!",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors

    def test_password_mismatch(self):
        """Şifreler eşleşmezse hata vermeli."""
        form = RegisterForm(
            data={
                "username": "testmismatch",
                "email": "mm@test.com",
                "password1": "GucluSifre123!",
                "password2": "FarkliSifre999!",
            }
        )
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_missing_email(self):
        """Email zorunlu alan."""
        form = RegisterForm(
            data={
                "username": "noemail",
                "email": "",
                "password1": "GucluSifre123!",
                "password2": "GucluSifre123!",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors

    def test_save_creates_user(self):
        """Form kaydedilince kullanıcı oluşmalı."""
        form = RegisterForm(
            data={
                "username": "kayituser",
                "email": "kayit@test.com",
                "password1": "GucluSifre123!",
                "password2": "GucluSifre123!",
            }
        )
        assert form.is_valid()
        user = form.save()
        assert User.objects.filter(username="kayituser").exists()
        assert user.email == "kayit@test.com"


class TestCustomLoginForm:
    """CustomLoginForm testleri."""

    def test_form_fields_exist(self):
        """Form'da username ve password alanları olmalı."""
        form = CustomLoginForm()
        assert "username" in form.fields
        assert "password" in form.fields

    def test_username_label(self):
        """Username label email/kullanıcı adı olmalı."""
        form = CustomLoginForm()
        assert "E-posta" in form.fields["username"].label

    def test_password_label(self):
        """Password label Şifre olmalı."""
        form = CustomLoginForm()
        assert form.fields["password"].label == "Şifre"


@pytest.mark.django_db
class TestProfileForm:
    """ProfileForm testleri."""

    def test_valid_data(self):
        """Geçerli profil verisi ile form valid olmalı."""
        user = User.objects.create_user(username="proftest", password="Test1234!")
        form = ProfileForm(
            data={
                "full_name": "Ali Veli",
                "phone": "+90 555 111 2233",
                "birth_date": "2000-01-15",
                "city": "Ankara",
                "bio": "Merhaba!",
            },
            instance=user.profile,
        )
        assert form.is_valid(), form.errors

    def test_save_updates_profile(self):
        """Form kaydedilince Profile güncellenmeli."""
        user = User.objects.create_user(username="savetest", password="Test1234!")
        form = ProfileForm(
            data={
                "full_name": "Mehmet Yılmaz",
                "phone": "",
                "birth_date": "",
                "city": "Malatya",
                "bio": "Test bio",
            },
            instance=user.profile,
        )
        assert form.is_valid()
        form.save()
        user.profile.refresh_from_db()
        assert user.profile.full_name == "Mehmet Yılmaz"
        assert user.profile.city == "Malatya"
        assert user.profile.bio == "Test bio"

    def test_all_fields_optional(self):
        """Profil alanlarının hepsi opsiyonel olmalı."""
        user = User.objects.create_user(username="opttest", password="Test1234!")
        form = ProfileForm(
            data={
                "full_name": "",
                "phone": "",
                "birth_date": "",
                "city": "",
                "bio": "",
            },
            instance=user.profile,
        )
        assert form.is_valid(), form.errors
