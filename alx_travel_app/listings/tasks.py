from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_success_email(user_email, booking_reference):
    send_mail(
        "Payment Confirmation",
        f"Your payment for booking {booking_reference} was successful.",
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
