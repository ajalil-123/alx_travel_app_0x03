from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from .tasks import send_booking_confirmation_email

@receiver(post_save, sender=Booking)
def trigger_booking_email(sender, instance, created, **kwargs):
    if created:
        # Send email asynchronously via Celery
        send_booking_confirmation_email.delay(
            instance.user.email,
            str(instance.booking_id)
        )
