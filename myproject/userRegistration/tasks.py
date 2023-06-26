from __future__ import absolute_import, unicode_literals

from celery import shared_task
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from celery.schedules import crontab
from django.utils import timezone
from time import sleep
from django.conf import settings

# @shared_task(bind=True)
# def send_everyday_mail(self, message):
#     recipient_list=[user.email]
#     mail_subject = "You are on your luck day!"
#     send_mail(
#         subject = mail_subject,
#         message=message,
#         from_email=settings.EMAIL_HOST_USER,
#         recipient_list=recipient_list,
#         fail_silently=False,
#         )
#     return "Done"

@shared_task(bind=True)
def send_everyday_mail(self):
    # Get the users who registered 1 day ago
    one_day_ago = timezone.now() - timedelta(days=1)
    new_users = User.objects.filter(date_joined__date=one_day_ago.date())

    # Send email to each new user
    for user in new_users:
        recipient_list = [user.email]
        mail_subject = "Welcome to Our Website!"
        message = f"Dear {user.username}, welcome to our website. We are glad to have you on board!"

        send_mail(
            subject=mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )

    return "Emails sent to new users"

@shared_task
def send_welcome_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        subject = 'Welcome to Our Website'
        message = f'Hi {user.username},\n\nThank you for joining our website. We are excited to have you on board!'
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        pass