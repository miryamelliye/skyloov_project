from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from your_app.tasks import send_welcome_email

# @receiver(post_save, sender=User)
# def schedule_welcome_email(sender, instance, created, **kwargs):
#     if created:
#         eta = datetime.now() + timedelta(days=1)
#         send_welcome_email.apply_async(args=[instance.id], eta=eta)
