"""
Email service for sending async emails.
Implements Single Responsibility Principle for email operations.
"""
import logging
from typing import List

from asgiref.sync import sync_to_async
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Centralized email service for all async email operations.
    Handles sending emails using Django's mail backend.
    """

    @staticmethod
    @sync_to_async
    def send_contact_email(subject: str, message: str, from_email: str, recipient_list: List[str]) -> int:
        """Send contact email using Django's send_mail backend."""
        return send_mail(subject, message, from_email, recipient_list, fail_silently=False)


# ========== Backward Compatibility Wrapper ==========

@sync_to_async
def send_contact_email(subject: str, message: str, from_email: str, recipient_list: List[str]) -> int:
    """Deprecated: Use EmailService.send_contact_email instead."""
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False)