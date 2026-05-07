"""
SOLD-OUT — apps.payments.forms
"""

import datetime
from django import forms
from django.core.exceptions import ValidationError

from .validators import luhn_check, detect_card_brand, validate_cvv, validate_expiry


class PaymentForm(forms.Form):
    card_number = forms.CharField(
        label="Kart Numarası",
        max_length=19,
        widget=forms.TextInput(
            attrs={
                "placeholder": "0000 0000 0000 0000",
                "class": "form-input w-full",
                "autocomplete": "cc-number",
                "inputmode": "numeric",
                "id": "id_card_number",
            }
        ),
    )
    card_holder = forms.CharField(
        label="Kart Üzerindeki İsim",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "AD SOYAD",
                "class": "form-input w-full uppercase",
                "autocomplete": "cc-name",
                "id": "id_card_holder",
            }
        ),
    )
    
    MONTH_CHOICES = [(f"{i:02d}", f"{i:02d}") for i in range(1, 13)]
    expiry_month = forms.ChoiceField(
        label="Ay",
        choices=[("", "Ay")] + MONTH_CHOICES,
        widget=forms.Select(attrs={"class": "form-input w-full", "id": "id_expiry_month"}),
    )
    
    current_year = datetime.datetime.now().year
    YEAR_CHOICES = [(str(i), str(i)) for i in range(current_year, current_year + 11)]
    expiry_year = forms.ChoiceField(
        label="Yıl",
        choices=[("", "Yıl")] + YEAR_CHOICES,
        widget=forms.Select(attrs={"class": "form-input w-full", "id": "id_expiry_year"}),
    )
    
    cvv = forms.CharField(
        label="CVV",
        max_length=4,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "•••",
                "class": "form-input w-full",
                "autocomplete": "cc-csc",
                "inputmode": "numeric",
                "id": "id_cvv",
            }
        ),
    )

    def clean_card_holder(self):
        holder = self.cleaned_data.get("card_holder", "").strip()
        # Sadece harfler ve boşluk kontrolü (Türkçe karakterler dahil)
        if not all(c.isalpha() or c.isspace() for c in holder):
            raise ValidationError("Kart üzerindeki isim sadece harf içerebilir.")
        return holder

    def clean_card_number(self):
        number = self.cleaned_data.get("card_number", "")
        # Boşlukları temizle
        clean_num = number.replace(" ", "").replace("-", "")
        
        if not clean_num.isdigit():
            raise ValidationError("Kart numarası sadece rakamlardan oluşmalıdır.")
            
        if not luhn_check(clean_num):
            raise ValidationError("Geçersiz kart numarası (Luhn hatası).")
            
        brand = detect_card_brand(clean_num)
        self.cleaned_data["card_brand"] = brand
        
        return clean_num

    def clean(self):
        cleaned_data = super().clean()
        
        card_number = cleaned_data.get("card_number")
        cvv = cleaned_data.get("cvv")
        brand = cleaned_data.get("card_brand")
        
        if card_number and cvv and brand:
            if not validate_cvv(cvv, brand):
                self.add_error("cvv", f"{brand} için geçersiz CVV uzunluğu.")
                
        month = cleaned_data.get("expiry_month")
        year = cleaned_data.get("expiry_year")
        
        if month and year:
            if not validate_expiry(month, year):
                self.add_error("expiry_month", "Kartın son kullanma tarihi geçmiş.")
                
        return cleaned_data
