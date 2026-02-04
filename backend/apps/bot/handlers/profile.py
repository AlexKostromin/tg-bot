"""
Обработчики редактирования профиля пользователя.
"""
from telegram import Update
from telegram.ext import ContextTypes

from ..states import EDIT_FIELD, EDIT_CHOICE, MORE_EDITS
from ..keyboards import get_edit_fields_keyboard, get_more_edits_keyboard
from ..messages import get_edit_prompt_message, get_field_prompts, get_field_updated_message
from ..utils.db import get_user_by_telegram_id, update_user_fields, create_profile_log
from .start import start


async def show_edit_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show which fields can be edited"""
    query = update.callback_query
    
    reply_markup = get_edit_fields_keyboard()
    text = get_edit_prompt_message()
    
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return EDIT_FIELD


async def edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle field editing"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel':
        return await start(update, context)
    
    field = query.data.split('_')[1]
    context.user_data['edit_field'] = field
    
    field_prompts = get_field_prompts()
    await query.edit_message_text(text=field_prompts.get(field))
    return EDIT_CHOICE


async def edit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle edited field input"""
    field = context.user_data.get('edit_field')
    new_value = update.message.text
    telegram_id = context.user_data.get('telegram_id')
    user = await get_user_by_telegram_id(telegram_id)
    
    field_mapping = {
        'phone': 'phone',
        'email': 'email',
        'city': 'city',
        'school': 'school',
        'certificate': 'certificate_name',
        'important': 'important_info'
    }
    
    if field == 'name':
        parts = new_value.split(maxsplit=1)
        old_first = user.first_name
        old_last = user.last_name
        new_first = parts[0] if parts else ''
        new_last = parts[1] if len(parts) > 1 else ''
        
        await update_user_fields(user, first_name=new_first, last_name=new_last)
        
        await create_profile_log(user, 'first_name', old_first, new_first)
        if len(parts) > 1:
            await create_profile_log(user, 'last_name', old_last, new_last)
    else:
        db_field = field_mapping.get(field)
        if db_field:
            old_value = getattr(user, db_field, None)
            await update_user_fields(user, **{db_field: new_value})
            
            if field == 'important':
                await create_profile_log(user, db_field, old_value, new_value)
    
    reply_markup = get_more_edits_keyboard()
    await update.message.reply_text(
        get_field_updated_message(),
        reply_markup=reply_markup
    )
    
    return MORE_EDITS


async def more_edits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle more edits choice"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'more_edits_yes':
        return await show_edit_options(update, context)
    else:
        # Локальный импорт, чтобы избежать циклического импорта с registration.py
        from .registration import confirm_existing_user

        telegram_id = context.user_data.get('telegram_id')
        user = await get_user_by_telegram_id(telegram_id)
        role = context.user_data.get('role')
        return await confirm_existing_user(update, context, user, role)
