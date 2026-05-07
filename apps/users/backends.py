"""
SOLD-OUT — apps.users.backends

EmailBackend: Email adresi ile giriş yapabilmeyi sağlayan
custom authentication backend. Django default User modeli ile çalışır.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Email veya username ile giriş yapabilmeyi sağlar.
    Önce email ile dener, bulamazsa username ile dener.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Önce email ile dene
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # Email bulunamadı, username ile dene
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
