"""
SOLD-OUT — apps.users.forms

RegisterForm       : Yeni kullanıcı kaydı (email unique)
CustomLoginForm    : Email veya username ile giriş
ProfileForm        : Profil bilgilerini güncelleme
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    """Kullanıcı kayıt formu — UserCreationForm üzerine email ekler."""

    email = forms.EmailField(
        required=True,
        label="E-posta Adresi",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "ornek@email.com",
                "class": "form-input",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": "Kullanıcı Adı",
        }
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "kullanici_adi",
                    "class": "form-input",
                    "autocomplete": "username",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Password alanlarını Türkçeleştir
        self.fields["password1"].label = "Şifre"
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "En az 8 karakter", "class": "form-input"}
        )
        self.fields["password2"].label = "Şifre (Tekrar)"
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Şifreyi tekrar girin", "class": "form-input"}
        )
        # Help text'leri temizle (UI'da ayrıca gösterilecek)
        for field in self.fields.values():
            field.help_text = None

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """Email veya username ile giriş formu."""

    username = forms.CharField(
        label="E-posta veya Kullanıcı Adı",
        widget=forms.TextInput(
            attrs={
                "placeholder": "ornek@email.com veya kullanici_adi",
                "class": "form-input",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Şifre",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "••••••••",
                "class": "form-input",
                "autocomplete": "current-password",
            }
        ),
    )


class ProfileForm(forms.ModelForm):
    """Profil bilgilerini güncelleme formu."""

    email = forms.EmailField(
        required=True,
        label="E-posta Adresi",
        widget=forms.EmailInput(
            attrs={"placeholder": "ornek@email.com", "class": "form-input"}
        )
    )

    class Meta:
        model = Profile
        fields = ("full_name", "email", "phone", "birth_date", "city", "bio", "profile_photo")
        labels = {
            "full_name": "Ad Soyad",
            "phone": "Telefon",
            "birth_date": "Doğum Tarihi",
            "city": "Şehir",
            "bio": "Hakkında",
            "profile_photo": "Profil Fotoğrafı",
        }
        widgets = {
            "full_name": forms.TextInput(
                attrs={"placeholder": "Ad Soyad", "class": "form-input"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "+90 5xx xxx xx xx", "class": "form-input"}
            ),
            "birth_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date", "class": "form-input"}
            ),
            "city": forms.TextInput(
                attrs={"placeholder": "İstanbul", "class": "form-input"}
            ),
            "bio": forms.Textarea(
                attrs={
                    "placeholder": "Kendinizden kısaca bahsedin...",
                    "class": "form-input",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            self.fields["email"].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            if User.objects.filter(email__iexact=email).exclude(id=self.instance.user.id).exists():
                raise forms.ValidationError("Bu e-posta adresi başka bir hesap tarafından kullanılıyor.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        email = self.cleaned_data.get("email")
        if email and profile.user:
            profile.user.email = email
            if commit:
                profile.user.save()
        if commit:
            profile.save()
        return profile
