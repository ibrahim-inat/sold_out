"""
SOLD-OUT — apps.orders.services
"""

import uuid
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment


class OrderCreationError(Exception):
    pass


class OrderService:
    @classmethod
    def _generate_order_number(cls) -> str:
        """SO-YYYYMMDD-XXXXX formatında eşsiz sipariş numarası üretir."""
        date_str = timezone.now().strftime("%Y%m%d")
        # Basit rastgele üretim, gerçekte seq kullanılabilir
        random_str = str(uuid.uuid4())[:5].upper()
        return f"SO-{date_str}-{random_str}"

    @classmethod
    def create_order_from_cart(cls, user, cart, billing_data: dict) -> Order:
        if not cart.items.exists():
            raise OrderCreationError("Sepet boş.")

        with transaction.atomic():
            # Siparişi oluştur
            order = Order.objects.create(
                order_number=cls._generate_order_number(),
                user=user,
                full_name=billing_data.get("full_name", ""),
                email=billing_data.get("email", ""),
                phone=billing_data.get("phone", ""),
                total_price=cart.total_price,
                status=Order.Status.PENDING
            )

            # Sepet öğelerini aktar ve kapasite kontrolü yap
            for item in cart.items.select_related("event"):
                event = item.event
                
                # Kapasite kontrolü (Yeniden)
                if event.tickets_sold + item.quantity > event.capacity:
                    # Hata durumunda sepet temizlenmesi isteniyorsa burada yapabiliriz.
                    # Ancak genellikle sepette kalır ve kullanıcıyı uyarır.
                    # Biz prompt'a göre "OrderCreationError fırlat" yapacağız.
                    raise OrderCreationError(
                        f"Kapasite yetersiz: {event.title} için sadece {event.available_tickets} bilet kaldı."
                    )
                
                OrderItem.objects.create(
                    order=order,
                    event=event,
                    quantity=item.quantity,
                    unit_price=event.price,
                    subtotal=item.subtotal
                )

            # Sepeti temizle
            cart.items.all().delete()
            
            return order

    @classmethod
    def process_payment(cls, order: Order, payment_data: dict) -> Payment:
        card_number = payment_data.get("card_number", "")
        card_brand = payment_data.get("card_brand", "UNKNOWN")
        last4 = card_number[-4:] if len(card_number) >= 4 else "0000"
        
        with transaction.atomic():
            payment = Payment.objects.create(
                order=order,
                amount=order.total_price,
                card_brand=card_brand,
                card_last4=last4,
                transaction_id=str(uuid.uuid4())
            )
            
            # SİMÜLASYON KURALLARI
            if last4 == "0000":
                payment.status = Payment.Status.FAILED
                payment.failure_reason = "Bakiye yetersiz"
                payment.save()
                
                order.status = Order.Status.FAILED
                order.save()
                return payment
                
            elif last4 == "1111":
                payment.status = Payment.Status.FAILED
                payment.failure_reason = "Kart reddedildi"
                payment.save()
                
                order.status = Order.Status.FAILED
                order.save()
                return payment
                
            # SUCCESS
            payment.status = Payment.Status.SUCCESS
            payment.paid_at = timezone.now()
            payment.save()
            
            order.status = Order.Status.PAID
            order.paid_at = timezone.now()
            order.save()
            
            # Event tickets_sold güncelle ve Biletleri oluştur
            from apps.tickets.models import Ticket, generate_unique_ticket_code
            
            tickets_to_create = []
            
            for item in order.items.all():
                event = item.event
                # Kapasite son kontrol (Concurrency için normalde F() objesi gerekir)
                from django.db.models import F
                event.tickets_sold = F('tickets_sold') + item.quantity
                event.save()
                
                # Biletleri listeye ekle
                for _ in range(item.quantity):
                    tickets_to_create.append(
                        Ticket(
                            order=order,
                            event=event,
                            ticket_code=generate_unique_ticket_code(),
                            holder_name=order.full_name
                        )
                    )
            
            # Bulk create biletler
            if tickets_to_create:
                Ticket.objects.bulk_create(tickets_to_create)
                
            # E-posta bildirimini gönder
            try:
                from apps.notifications.services import EmailService
                EmailService.send_order_confirmation_email(order)
            except Exception:
                pass # Mail atılamasa bile ödeme başarılı sayılır
                
            return payment
