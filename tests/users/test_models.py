"""
SOLD-OUT — tests/users/test_models.py

Profile, Organizer model ve signal testleri.
"""

import pytest
from django.contrib.auth.models import User

from apps.users.models import Organizer, Profile


@pytest.mark.django_db
class TestProfileModel:
    """Profile model testleri."""

    def test_profile_auto_created_on_user_create(self):
        """Yeni kullanıcı oluşturulduğunda Profile otomatik yaratılmalı."""
        user = User.objects.create_user(
            username="signaltest",
            email="signal@test.com",
            password="TestPass123!",
        )
        assert hasattr(user, "profile")
        assert isinstance(user.profile, Profile)

    def test_profile_str(self):
        """Profile.__str__ doğru format döndürmeli."""
        user = User.objects.create_user(username="strtest", password="TestPass123!")
        assert str(user.profile) == "strtest — Profil"

    def test_profile_fields_default_blank(self):
        """Yeni profilde phone, city, bio, full_name boş; birth_date None olmalı."""
        user = User.objects.create_user(username="blanktest", password="TestPass123!")
        profile = user.profile
        assert profile.phone == ""
        assert profile.city == ""
        assert profile.full_name == ""
        assert profile.bio == ""
        assert profile.birth_date is None
        assert not profile.profile_photo  # ImageField boşken falsy

    def test_profile_update_fields(self):
        """Profile alanları güncellenebilmeli."""
        user = User.objects.create_user(username="updatetest", password="TestPass123!")
        profile = user.profile
        profile.full_name = "Test Kullanıcı"
        profile.phone = "+90 555 123 4567"
        profile.city = "İstanbul"
        profile.bio = "Merhaba dünya!"
        profile.save()
        profile.refresh_from_db()
        assert profile.full_name == "Test Kullanıcı"
        assert profile.phone == "+90 555 123 4567"
        assert profile.city == "İstanbul"
        assert profile.bio == "Merhaba dünya!"

    def test_profile_meta_ordering(self):
        """Profile Meta ordering -created_at olmalı."""
        assert Profile._meta.ordering == ["-created_at"]

    def test_profile_verbose_name(self):
        """Profile verbose_name Türkçe olmalı."""
        assert Profile._meta.verbose_name == "Profil"
        assert Profile._meta.verbose_name_plural == "Profiller"


@pytest.mark.django_db
class TestOrganizerModel:
    """Organizer model testleri."""

    def test_organizer_create(self):
        """Organizer oluşturulabilmeli."""
        user = User.objects.create_user(username="orguser", password="TestPass123!")
        org = Organizer.objects.create(
            user=user,
            organization_name="Test Etkinlik AŞ",
            about="Test organizasyon",
        )
        assert org.organization_name == "Test Etkinlik AŞ"
        assert org.is_verified is False

    def test_organizer_str_unverified(self):
        """Onaysız organizatörün __str__'i ✗ içermeli."""
        user = User.objects.create_user(username="orgstr", password="TestPass123!")
        org = Organizer.objects.create(user=user, organization_name="Müzik Co")
        assert "✗" in str(org)
        assert "Müzik Co" in str(org)

    def test_organizer_str_verified(self):
        """Onaylı organizatörün __str__'i ✓ içermeli."""
        user = User.objects.create_user(username="orgver", password="TestPass123!")
        org = Organizer.objects.create(
            user=user, organization_name="Konser Ltd", is_verified=True
        )
        assert "✓" in str(org)

    def test_organizer_verbose_name(self):
        """Organizer verbose_name Türkçe olmalı."""
        assert Organizer._meta.verbose_name == "Organizatör"
        assert Organizer._meta.verbose_name_plural == "Organizatörler"

    def test_organizer_meta_ordering(self):
        """Organizer Meta ordering -created_at olmalı."""
        assert Organizer._meta.ordering == ["-created_at"]
