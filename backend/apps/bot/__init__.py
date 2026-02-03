"""
Точка входа для настройки Telegram-бота.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)
from telegram.error import TelegramError, RetryAfter
from django.conf import settings

from .states import (
    START,
    CONTACT_MESSAGE,
    COMPETITION_SELECT,
    ROLE_SELECT,
    CONFIRM_DATA,
    EDIT_FIELD,
    EDIT_CHOICE,
    MORE_EDITS,
    NEW_USER_NAME,
    NEW_USER_SURNAME,
    NEW_USER_PHONE,
    NEW_USER_EMAIL,
    NEW_USER_BIRTH_DATE,
    NEW_USER_COUNTRY,
    NEW_USER_CITY,
    NEW_USER_SCHOOL,
    NEW_USER_CHANNEL_NAME,
    NEW_USER_CERT_ROLE,
    NEW_USER_CERT_NAME,
    NEW_USER_COMPANY,
    NEW_USER_POSITION,
    NEW_USER_IMPORTANT,
    VOTER_SLOT_DATE,
    VOTER_SLOT_START,
    VOTER_SLOT_END,
)
from .constants import (
    PATTERN_COMPETITION, PATTERN_ROLE, PATTERN_CONFIRM,
    PATTERN_EDIT_FIELD, PATTERN_MORE_EDITS, PATTERN_CERT_CHOICE,
    PATTERN_MAIN_MENU,
)
from .handlers.start import start, button_start
from .handlers.contact import contact_message_handler, contact_message
from .handlers.registration import (
    show_competitions,
    select_competition,
    show_roles,
    select_role,
    confirm_existing_user,
    confirm_choice,
    register_new_user_start,
    new_user_name,
    new_user_surname,
    new_user_phone,
    new_user_email,
    new_user_birth_date,
    new_user_country,
    new_user_city,
    new_user_school,
    new_user_cert_choice,
    new_user_cert_name,
    new_user_channel_name,
    new_user_company,
    new_user_position,
    new_user_important,
    voter_slot_date,
    voter_slot_start,
    voter_slot_end,
)
from .handlers.profile import show_edit_options, edit_field, edit_input, more_edits

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def cancel(update, context):
    """Fallback handler для отмены операции."""
    from .messages import get_cancel_message
    from .handlers.start import start
    
    await update.message.reply_text(get_cancel_message())
    return await start(update, context)


def setup_bot_handlers(app: Application) -> None:
    """Setup all bot handlers with conversation"""
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [
                CallbackQueryHandler(button_start, pattern=PATTERN_MAIN_MENU),
            ],
            CONTACT_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, contact_message),
            ],
            COMPETITION_SELECT: [
                CallbackQueryHandler(select_competition, pattern=PATTERN_COMPETITION),
            ],
            ROLE_SELECT: [
                CallbackQueryHandler(select_role, pattern=PATTERN_ROLE),
            ],
            CONFIRM_DATA: [
                CallbackQueryHandler(confirm_choice, pattern=PATTERN_CONFIRM),
            ],
            EDIT_FIELD: [
                CallbackQueryHandler(edit_field, pattern=PATTERN_EDIT_FIELD),
            ],
            EDIT_CHOICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_input),
            ],
            MORE_EDITS: [
                CallbackQueryHandler(more_edits, pattern=PATTERN_MORE_EDITS),
            ],
            NEW_USER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_name),
            ],
            NEW_USER_SURNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_surname),
            ],
            NEW_USER_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_phone),
            ],
            NEW_USER_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_email),
            ],
            NEW_USER_BIRTH_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_birth_date),
            ],
            NEW_USER_COUNTRY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_country),
            ],
            NEW_USER_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_city),
            ],
            NEW_USER_SCHOOL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_school),
            ],
            NEW_USER_CHANNEL_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_channel_name),
            ],
            NEW_USER_CERT_ROLE: [
                CallbackQueryHandler(new_user_cert_choice, pattern=PATTERN_CERT_CHOICE),
            ],
            NEW_USER_CERT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_cert_name),
            ],
            NEW_USER_COMPANY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_company),
            ],
            NEW_USER_POSITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_position),
            ],
            NEW_USER_IMPORTANT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_user_important),
            ],
            VOTER_SLOT_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, voter_slot_date),
            ],
            VOTER_SLOT_START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, voter_slot_start),
            ],
            VOTER_SLOT_END: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, voter_slot_end),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(conv_handler)

    # Фоновая обработка outbox-рассылок (Telegram)
    try:
        interval = getattr(settings, 'BOT_OUTBOX_POLL_SECONDS', 2)
        app.job_queue.run_repeating(_process_outbox_job, interval=interval, first=2, name='outbox')
    except Exception:
        logger.exception("Failed to schedule outbox job")


async def _process_outbox_job(context) -> None:
    """
    JobQueue callback: читает pending outbox и отправляет сообщения через Telegram API.
    """
    from .utils.db import get_pending_outbox, mark_outbox_sent, mark_outbox_failed

    batch_size = getattr(settings, 'BOT_OUTBOX_BATCH_SIZE', 50)
    max_attempts = getattr(settings, 'BOT_OUTBOX_MAX_ATTEMPTS', 10)

    items = await get_pending_outbox(batch_size)
    if not items:
        return

    bot = context.application.bot
    for item in items:
        attempts = (item.attempts or 0) + 1
        try:
            await bot.send_message(chat_id=item.chat_id, text=item.message)
            await mark_outbox_sent(item.id)
        except RetryAfter as e:
            # Уважим rate limit: увеличим attempts и оставим pending
            await mark_outbox_failed(item.id, f"RetryAfter: {e}", attempts, max_attempts)
        except TelegramError as e:
            await mark_outbox_failed(item.id, f"TelegramError: {e}", attempts, max_attempts)
        except Exception as e:
            await mark_outbox_failed(item.id, f"Exception: {e}", attempts, max_attempts)
