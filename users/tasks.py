import logging
from celery import shared_task
from django.conf import settings


logger = logging.getLogger(__name__)

@shared_task
def send_email_task_celery(subject, message, recipient_list):
    from django.core.mail import send_mail
    logger.info('Start sending email')
    sent_count = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )
    if sent_count:
        return f"Successfully sent email to {recipient_list[0]}"
    return "Failed to send email"


def send_email_task_default(subject, message, recipient_list):
    from django.core.mail import send_mail
    logger.info('Start sending email')
    sent_count = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )
    if sent_count:
        return f"Successfully sent email to {recipient_list[0]}"
    return "Failed to send email"

