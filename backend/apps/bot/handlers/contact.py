"""
Обработчики связи с командой USN.
"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

from ..states import CONTACT_MESSAGE
from ..messages import BotMessages
from ..utils.email import send_contact_email
from .start import start
from django.conf import settings

logger = logging.getLogger(__name__)


async def contact_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show contact prompt"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=BotMessages.contact_prompt())
    return CONTACT_MESSAGE


async def contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle contact message"""
    message_text = update.message.text
    user = update.effective_user
    chat_id = str(update.effective_chat.id) if update.effective_chat else 'unknown'

    logger.info(f"Message from {user.username} ({user.id}): {message_text}")
    # Forward message to contact email
    subject = f"USN contact message from @{user.username or user.id}"
    body = f"From: @{user.username or '—'} (id: {user.id}, chat_id: {chat_id})\n\n{message_text}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost')

    email_sent = False
    try:
        await send_contact_email(subject, body, from_email, [settings.CONTACT_EMAIL_TO])
        email_sent = True
    except Exception as exc:
        logger.exception('Failed to send contact email: %s', exc)
        # Notify user that email failed to send
        await update.message.reply_text(
            "⚠️ Не удалось отправить сообщение на email.\n"
            "Сообщение сохранено и будет обработано администратором позже."
        )

    if email_sent:
        await update.message.reply_text(BotMessages.contact_success())

    return await start(update, context)
