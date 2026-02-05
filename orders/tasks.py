from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email_order_task(subject, text_content, html_content, email):
    msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=email
        )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
    return 'Successfully sent email'
