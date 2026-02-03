"""
Обработчики команды /start и главного меню.
"""
from telegram import Update
from telegram.ext import ContextTypes

from ..states import START
from ..keyboards import get_main_menu_keyboard
from ..messages import get_welcome_message
from ..utils.db import get_or_create_user

# уточнить будет ли эта функция работать асинхронно, если в ней get_or_create_user уже с
# декоратором для синхронной работы, стоил ли сделать саму функцию start синхронной
# класс который отвечает за типовые операции


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - show main menu"""
    user = update.effective_user
    chat_id = str(update.effective_chat.id)

    create_user = DB() # подумать над созданием класса, который отвечает за взаимодейстивие с БД
    # Save/update basic user info


    await get_or_create_user(
        chat_id=chat_id,
        telegram_id=str(user.id),
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    
    reply_markup = get_main_menu_keyboard()
    message_text = get_welcome_message()
    
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
        # точно ли этот импорт нельзя вынести наверх ко всеем остальным
        from .contact import contact_message_handler

        return await contact_message_handler(update, context)
    
    elif query.data == 'register_competition':
        from .registration import show_competitions
        context.user_data['telegram_id'] = str(update.effective_user.id)
        context.user_data['chat_id'] = str(update.effective_chat.id)
        return await show_competitions(update, context)
