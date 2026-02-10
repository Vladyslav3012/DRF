from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_email_task_default

User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        subject = "Your gmail has been register on our website"
        message = (f"Hello {instance.username} .{subject}, nice to meet you!\n"
                   f"You code to activate email: {instance.otp} ")
        to_email = instance.email
        send_email_task_default(subject, message, [to_email])
