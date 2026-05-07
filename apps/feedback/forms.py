"""
SOLD-OUT — apps.feedback.forms
"""

from django import forms
from .models import Comment, Feedback


class CommentForm(forms.ModelForm):
    # Yıldızlar UI'da yönetilecek, form tarafında basit IntegerField kullanıyoruz
    rating = forms.IntegerField(
        min_value=1, max_value=5,
        widget=forms.HiddenInput(attrs={"id": "rating-input"}),
        error_messages={'min_value': 'Lütfen bir puan seçin.', 'max_value': 'Geçersiz puan.'}
    )
    
    class Meta:
        model = Comment
        fields = ["comment", "rating"]
        widgets = {
            "comment": forms.Textarea(attrs={
                "class": "w-full rounded-xl border-gray-200 focus:border-indigo-500 focus:ring-indigo-500",
                "rows": 4,
                "placeholder": "Etkinlik hakkındaki düşüncelerinizi paylaşın..."
            })
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["category", "rating", "comment"]
        widgets = {
            "category": forms.Select(attrs={
                "class": "w-full rounded-xl border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
            }),
            "rating": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border-gray-200 focus:border-indigo-500 focus:ring-indigo-500",
                "min": 1, "max": 5
            }),
            "comment": forms.Textarea(attrs={
                "class": "w-full rounded-xl border-gray-200 focus:border-indigo-500 focus:ring-indigo-500",
                "rows": 5,
                "placeholder": "Detaylı geri bildiriminiz..."
            })
        }
