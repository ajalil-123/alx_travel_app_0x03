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


from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id, user_email, user_name, listing_title, check_in, check_out):
    """
    Send booking confirmation email asynchronously
    """
    try:
        # Email subject
        subject = f'Booking Confirmation - {listing_title}'
        
        # Email context
        context = {
            'user_name': user_name,
            'listing_title': listing_title,
            'check_in': check_in,
            'check_out': check_out,
            'booking_id': booking_id,
        }
        
        # Create email content
        html_message = f"""
        <html>
        <body>
            <h2>Booking Confirmation</h2>
            <p>Dear {user_name},</p>
            <p>Your booking has been confirmed!</p>
            <p><strong>Details:</strong></p>
            <ul>
                <li>Booking ID: {booking_id}</li>
                <li>Property: {listing_title}</li>
                <li>Check-in: {check_in}</li>
                <li>Check-out: {check_out}</li>
            </ul>
            <p>Thank you for choosing our service!</p>
            <p>Best regards,<br>ALX Travel App Team</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Booking confirmation email sent successfully to {user_email} for booking {booking_id}")
        return f"Email sent successfully to {user_email}"
        
    except Exception as exc:
        logger.error(f"Error sending email for booking {booking_id}: {str(exc)}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def send_booking_reminder_email(booking_id, user_email, user_name, listing_title, check_in):
    """
    Send booking reminder email (can be used for scheduled reminders)
    """
    try:
        subject = f'Booking Reminder - {listing_title}'
        
        message = f"""
        Dear {user_name},
        
        This is a friendly reminder about your upcoming booking:
        
        Property: {listing_title}
        Check-in Date: {check_in}
        Booking ID: {booking_id}
        
        We look forward to hosting you!
        
        Best regards,
        ALX Travel App Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        logger.info(f"Booking reminder email sent to {user_email} for booking {booking_id}")
        return f"Reminder email sent to {user_email}"
        
    except Exception as exc:
        logger.error(f"Error sending reminder email for booking {booking_id}: {str(exc)}")
        raise exc