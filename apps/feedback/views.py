"""
SOLD-OUT — apps.feedback.views
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy

from apps.events.models import Event
from apps.orders.models import Order
from .models import Comment, Feedback
from .forms import CommentForm, FeedbackForm


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, event_slug):
        event = get_object_or_404(Event, slug=event_slug)
        
        # Kullanıcı bu etkinlik için başarılı bir bilet almış mı kontrol et
        has_ticket = Order.objects.filter(
            user=request.user, 
            status="PAID", 
            items__event=event
        ).exists()
        
        if not has_ticket:
            messages.error(request, "Yorum yapabilmek için bilet sahibi olmalısınız.")
            return redirect("events:detail", slug=event.slug)

        form = CommentForm(request.POST)
        if form.is_valid():
            # Yorum daha önce yapılmışsa güncelle, yoksa oluştur
            comment_obj, created = Comment.objects.update_or_create(
                user=request.user,
                event=event,
                defaults={
                    "comment": form.cleaned_data["comment"],
                    "rating": form.cleaned_data["rating"],
                }
            )
            if created:
                messages.success(request, "Yorumunuz başarıyla eklendi!")
            else:
                messages.success(request, "Yorumunuz güncellendi!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
                    
        return redirect("events:detail", slug=event.slug)


class DeleteCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        event_slug = comment.event.slug
        comment.delete()
        messages.success(request, "Yorumunuz silindi.")
        return redirect("events:detail", slug=event_slug)


class FeedbackView(FormView):
    template_name = "feedback/feedback_form.html"
    form_class = FeedbackForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        feedback = form.save(commit=False)
        if self.request.user.is_authenticated:
            feedback.user = self.request.user
        feedback.save()
        messages.success(self.request, "Geri bildiriminiz için teşekkür ederiz!")
        return super().form_valid(form)
