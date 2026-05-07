"""
SOLD-OUT — apps.notifications.services
"""

import threading
from smtplib import SMTPException
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import EmailLog


class EmailService:
    
    @classmethod
    def _send_sync(cls, template_name: str, context: dict, to_email: str, subject: str, user=None):
        """Asıl gönderimi yapan senkron metod"""
        # Context içerisine genel değişkenler ekle
        # Not: Site nesnesini kullanabilmek için 'django.contrib.sites' app'i gerekebilir, 
        # MVP'de basit bir site_url geçebiliriz
        site_url = "http://localhost:8000" if settings.DEBUG else "https://soldout.com"
        context["site_url"] = site_url
        context["site_name"] = "SOLD-OUT"

        html_content = render_to_string(f"emails/{template_name}.html", context)
        text_content = render_to_string(f"emails/{template_name}.txt", context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")

        # Log nesnesini baştan oluştur
        log = EmailLog(
            user=user,
            to_email=to_email,
            subject=subject,
            template_name=template_name,
        )

        try:
            msg.send()
            log.status = EmailLog.Status.SENT
        except Exception as e:
            # SMTPException veya diğer bağlantı hataları
            log.status = EmailLog.Status.FAILED
            log.error_message = str(e)
        finally:
            log.save()
            
        return log

    @classmethod
    def send_async(cls, template_name: str, context: dict, to_email: str, subject: str, user=None):
        """İsteği bloklamamak için threading kullanan asenkron mail gönderimi."""
        # Django testlerinde outbox'ın dolması için senkron çalışması avantajlıdır.
        # Bu yüzden test anında (kötü bir pratik olsa da MVP için) senkron çalıştırabiliriz 
        # veya pytest.mark.django_db(transaction=True) ile yönetebiliriz.
        import sys
        if 'pytest' in sys.modules:
            return cls._send_sync(template_name, context, to_email, subject, user)
            
        thread = threading.Thread(
            target=cls._send_sync,
            args=(template_name, context, to_email, subject, user),
            daemon=True # Main thread kapanınca mail thread'i de kapansın (dev server için)
        )
        thread.start()

    @classmethod
    def send_welcome_email(cls, user):
        context = {
            "user": user,
            "username": user.username,
        }
        cls.send_async(
            template_name="welcome",
            context=context,
            to_email=user.email,
            subject="SOLD-OUT'a Hoş Geldin!",
            user=user
        )

    @classmethod
    def send_order_confirmation_email(cls, order):
        # Siparişe ait biletleri al
        tickets = order.tickets.select_related("event").all()
        
        context = {
            "order": order,
            "tickets": tickets,
            "full_name": order.full_name,
            "order_number": order.order_number,
        }
        
        cls.send_async(
            template_name="order_confirmation",
            context=context,
            to_email=order.email,
            subject=f"Sipariş Onayı - #{order.order_number}",
            user=order.user
        )
