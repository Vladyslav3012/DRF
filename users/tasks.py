from celery import shared_task
from django.conf import settings


@shared_task
def send_email_task(subject, message, recipient_list):
    from django.core.mail import send_mail
    sent_count = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )
    if sent_count:
        return f"Successfully sent email to {recipient_list[0]}"
    return "Failed to send email"
