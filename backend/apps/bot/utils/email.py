"""
Утилиты для отправки email.
"""
from asgiref.sync import sync_to_async
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# типы

@sync_to_async
def send_contact_email(subject, message, from_email, recipient_list):
    """Send contact email using Django's send_mail"""
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False)
