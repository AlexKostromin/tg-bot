"""
Обработчики команды /start и главного меню.
"""
from telegram import Update
from telegram.ext import ContextTypes

from ..states import START
from ..keyboards import get_main_menu_keyboard
from ..messages import BotMessages
from ..utils.db import get_or_create_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - show main menu"""
    user = update.effective_user
    chat_id = str(update.effective_chat.id)

    try:
        await get_or_create_user(
            chat_id=chat_id,
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Error creating user for /start: {e}")
        error_msg = "❌ Ошибка подключения к серверу. Пожалуйста, попробуйте позже."
        if update.message:
            await update.message.reply_text(error_msg)
        elif update.callback_query:
            await update.callback_query.answer(error_msg, show_alert=True)
        return START

    reply_markup = get_main_menu_keyboard()
    message_text = BotMessages.welcome()

    # Handle both message (/start) and callback query cases
    if update.message:
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text=message_text, reply_markup=reply_markup)

    return START


async def button_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'contact_usn':
        from .contact import contact_message_handler

        return await contact_message_handler(update, context)
    
    elif query.data == 'register_competition':
        from .registration import show_competitions
        context.user_data['telegram_id'] = str(update.effective_user.id)
        context.user_data['chat_id'] = str(update.effective_chat.id)
        return await show_competitions(update, context)
