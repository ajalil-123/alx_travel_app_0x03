from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_payment_success_email(user_email, booking_reference):
    """Send payment success email"""
    try:
        send_mail(
            "Payment Confirmation",
            f"Your payment for booking {booking_reference} was successful.",
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Payment success email sent to {user_email}")
        return f"Payment email sent to {user_email}"
    except Exception as e:
        logger.error(f"Failed to send payment email: {str(e)}")
        raise


from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation_email(user_email, booking_id):
    subject = "Booking Confirmation"
    message = f"Thank you for booking with us! Your booking ID is {booking_id}."
    sender = settings.EMAIL_HOST_USER

    send_mail(subject, message, sender, [user_email], fail_silently=False)
    return f"Booking confirmation email sent to {user_email}"



# from celery import shared_task
# from django.core.mail import send_mail

# @shared_task
# def send_booking_confirmation_email(user_email, booking_id, user_name=None, listing_name=None, start_date=None, end_date=None):
#     if not all([user_email, booking_id, listing_name, start_date, end_date]):
#         print("Missing required info, email not sent")
#         return
    
#     subject = "Booking Confirmation"
#     message = f"""
# Dear {user_name or 'Valued Customer'},

# Thank you for your booking with ALX Travel App!

# Booking Details:
# - Booking ID: {booking_id}
# - Property: {listing_name}
# - Check-in: {start_date}
# - Check-out: {end_date}

# We look forward to hosting you!

# Best regards,
# ALX Travel App Team
# """
#     send_mail(subject, message, 'abduljalilzakaria1@gmail.com', [user_email], fail_silently=False)
