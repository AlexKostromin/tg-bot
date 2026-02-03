"""
Обработчики регистрации на соревнования.
"""
from telegram import Update
from telegram.ext import ContextTypes
from apps.users.models import User
from datetime import datetime, date, time

from ..states import (
    COMPETITION_SELECT,
    ROLE_SELECT,
    CONFIRM_DATA,
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
from ..keyboards import (
    get_competitions_keyboard, get_roles_keyboard, get_confirmation_keyboard,
    get_certificate_choice_keyboard,
)
from ..messages import (
    get_no_competitions_message,
    get_competition_selection_message,
    get_role_selection_message,
    get_user_confirmation_message,
    get_registration_success_message,
    get_new_user_registration_success,
    get_new_user_name_prompt,
    get_new_user_surname_prompt,
    get_new_user_phone_prompt,
    get_new_user_email_prompt,
    get_new_user_birth_date_prompt,
    get_new_user_country_prompt,
    get_new_user_city_prompt,
    get_new_user_school_prompt,
    get_new_user_channel_name_prompt,
    get_certificate_question,
    get_certificate_name_prompt,
    get_company_prompt,
    get_position_prompt,
    get_important_info_prompt,
    get_voter_slot_date_prompt,
    get_voter_slot_start_prompt,
    get_voter_slot_end_prompt,
    get_voter_slot_saved_message,
)
from ..utils.db import (
    get_competitions,
    get_competition_by_id,
    get_user_by_telegram_id,
    add_user_to_competition,
    update_or_create_new_user,
    create_voter_time_slot,
)
from .start import start
from .profile import show_edit_options


async def show_competitions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available competitions"""
    query = update.callback_query if update.callback_query else None
    
    competitions = await get_competitions()
    
    if not competitions:
        text = get_no_competitions_message()
        if query:
            await query.edit_message_text(text=text)
        else:
            await update.message.reply_text(text)
        return await start(update, context)
    
    if len(competitions) == 1:
        context.user_data['competition_id'] = competitions[0].id
        context.user_data['competition_name'] = competitions[0].name
        return await show_roles(update, context)
    
    reply_markup = get_competitions_keyboard(competitions)
    text = get_competition_selection_message()
    
    if query:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    return COMPETITION_SELECT


async def select_competition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle competition selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel':
        return await start(update, context)
    
    comp_id = int(query.data.split('_')[1])
    comp = await get_competition_by_id(comp_id)
    
    context.user_data['competition_id'] = comp.id
    context.user_data['competition_name'] = comp.name
    
    return await show_roles(update, context)


async def show_roles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available roles for competition"""
    query = update.callback_query if update.callback_query else None
    
    comp_id = context.user_data.get('competition_id')
    comp = await get_competition_by_id(comp_id)
    
    reply_markup = get_roles_keyboard()
    text = get_role_selection_message()
    
    if query:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    return ROLE_SELECT


async def select_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle role selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel':
        return await start(update, context)
    
    role = query.data.split('_')[1]
    context.user_data['role'] = role
    
    telegram_id = context.user_data.get('telegram_id')
    
    try:
        user = await get_user_by_telegram_id(telegram_id)
        return await confirm_existing_user(update, context, user, role)
    except User.DoesNotExist:
        return await register_new_user_start(update, context)


async def confirm_existing_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, role: str) -> int:
    """Show existing user data for confirmation"""
    query = update.callback_query
    
    text = get_user_confirmation_message(user, role)
    reply_markup = get_confirmation_keyboard()
    
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return CONFIRM_DATA


async def confirm_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle confirmation choice"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_yes':
        telegram_id = context.user_data.get('telegram_id')
        user = await get_user_by_telegram_id(telegram_id)
        role = context.user_data.get('role')
        comp_id = context.user_data.get('competition_id')
        comp_name = context.user_data.get('competition_name')

        comp = await get_competition_by_id(comp_id)
        await add_user_to_competition(user, comp, role)

        # Для судей запускаем дополнительный сценарий выбора слота
        if role == 'voter':
            return await start_voter_timeslot_flow(update, context, user, comp_id)

        text = get_registration_success_message(role, comp_name)
        await query.edit_message_text(text=text)

        return await start(update, context)

    else:
        return await show_edit_options(update, context)


# Новые пользователи
async def register_new_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start new user registration"""
    query = update.callback_query
    await query.edit_message_text(text=get_new_user_name_prompt())
    return NEW_USER_NAME


async def new_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['first_name'] = update.message.text
    await update.message.reply_text(get_new_user_surname_prompt())
    return NEW_USER_SURNAME


async def new_user_surname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['last_name'] = update.message.text
    await update.message.reply_text(get_new_user_phone_prompt())
    return NEW_USER_PHONE


async def new_user_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(get_new_user_email_prompt())
    return NEW_USER_EMAIL


async def new_user_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    await update.message.reply_text(get_new_user_birth_date_prompt())
    return NEW_USER_BIRTH_DATE


async def new_user_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() == 'нет' or text == '-':
        context.user_data['birth_date'] = None
    else:
        try:
            parsed = datetime.strptime(text, "%Y-%m-%d").date()
            context.user_data['birth_date'] = parsed
        except ValueError:
            await update.message.reply_text(
                "Не удалось распознать дату. Пожалуйста, используйте формат ГГГГ-ММ-ДД, например 2010-05-23."
            )
            return NEW_USER_BIRTH_DATE

    await update.message.reply_text(get_new_user_country_prompt())
    return NEW_USER_COUNTRY


async def new_user_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['country'] = update.message.text
    await update.message.reply_text(get_new_user_city_prompt())
    return NEW_USER_CITY


async def new_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['city'] = update.message.text
    await update.message.reply_text(get_new_user_school_prompt())
    return NEW_USER_SCHOOL


async def new_user_school(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['school'] = update.message.text
    
    role = context.user_data.get('role')
    
    if role in ['player', 'voter']:
        reply_markup = get_certificate_choice_keyboard()
        await update.message.reply_text(
            get_certificate_question(),
            reply_markup=reply_markup
        )
        return NEW_USER_CERT_ROLE
    else:
        await update.message.reply_text(get_new_user_channel_name_prompt())
        return NEW_USER_CHANNEL_NAME


async def new_user_cert_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cert_yes':
        await query.edit_message_text(get_certificate_name_prompt())
        return NEW_USER_CERT_NAME
    else:
        await query.edit_message_text(get_company_prompt())
        return NEW_USER_COMPANY


async def new_user_cert_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['certificate_name'] = update.message.text
    await update.message.reply_text(get_new_user_channel_name_prompt())
    return NEW_USER_CHANNEL_NAME


async def new_user_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.text.strip()
    if raw.lower() in ('нет', 'no', '-'):
        context.user_data['channel_name'] = None
    else:
        context.user_data['channel_name'] = raw
    await update.message.reply_text(get_company_prompt())
    return NEW_USER_COMPANY


async def new_user_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['company'] = update.message.text
    await update.message.reply_text(get_position_prompt())
    return NEW_USER_POSITION


async def new_user_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['position'] = update.message.text
    
    role = context.user_data.get('role')
    if role in ['player', 'voter']:
        await update.message.reply_text(get_important_info_prompt())
        return NEW_USER_IMPORTANT
    else:
        return await finalize_new_user(update, context)


async def new_user_important(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['important_info'] = update.message.text
    return await finalize_new_user(update, context)


async def finalize_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = context.user_data.get('chat_id')
    telegram_id = context.user_data.get('telegram_id')
    
    user = await update_or_create_new_user(
        chat_id=chat_id,
        telegram_id=telegram_id,
        first_name=context.user_data.get('first_name'),
        last_name=context.user_data.get('last_name'),
        phone=context.user_data.get('phone'),
        email=context.user_data.get('email'),
        country=context.user_data.get('country'),
        city=context.user_data.get('city'),
        school=context.user_data.get('school'),
        company=context.user_data.get('company'),
        position=context.user_data.get('position'),
        certificate_name=context.user_data.get('certificate_name'),
        important_info=context.user_data.get('important_info'),
        birth_date=context.user_data.get('birth_date'),
        channel_name=context.user_data.get('channel_name'),
    )
    
    role = context.user_data.get('role')
    comp_id = context.user_data.get('competition_id')
    comp_name = context.user_data.get('competition_name')
    comp = await get_competition_by_id(comp_id)
    
    await add_user_to_competition(user, comp, role)

    # Для судей сразу запускаем сценарий слотов
    if role == 'voter':
        return await start_voter_timeslot_flow(update, context, user, comp_id)

    text = get_new_user_registration_success(user, role, comp_name)
    await update.message.reply_text(text)
    return await start(update, context)


async def start_voter_timeslot_flow(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    competition_id: int,
) -> int:
    """
    Старт сценария выбора временного слота для судьи.
    """
    context.user_data['voter_user_id'] = user.id
    context.user_data['voter_competition_id'] = competition_id

    # В зависимости от того, пришли мы из callback или message, отвечаем в нужный канал
    if getattr(update, "callback_query", None):
        await update.callback_query.edit_message_text(get_voter_slot_date_prompt())
    else:
        await update.message.reply_text(get_voter_slot_date_prompt())
    return VOTER_SLOT_DATE


async def voter_slot_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text_value = update.message.text.strip()
    try:
        parsed_date = datetime.strptime(text_value, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text(
            "Не получилось распознать дату.\n"
            "Пожалуйста, используйте формат ГГГГ-ММ-ДД, например 2026-03-15."
        )
        return VOTER_SLOT_DATE

    context.user_data['voter_slot_date'] = parsed_date
    await update.message.reply_text(get_voter_slot_start_prompt())
    return VOTER_SLOT_START


async def voter_slot_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text_value = update.message.text.strip()
    try:
        parsed_time = datetime.strptime(text_value, "%H:%M").time()
    except ValueError:
        await update.message.reply_text(
            "Не удалось распознать время.\n"
            "Пожалуйста, используйте формат ЧЧ:ММ, например 10:00."
        )
        return VOTER_SLOT_START

    context.user_data['voter_slot_start'] = parsed_time
    await update.message.reply_text(get_voter_slot_end_prompt())
    return VOTER_SLOT_END


async def voter_slot_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text_value = update.message.text.strip()
    try:
        parsed_time = datetime.strptime(text_value, "%H:%M").time()
    except ValueError:
        await update.message.reply_text(
            "Не удалось распознать время.\n"
            "Пожалуйста, используйте формат ЧЧ:ММ, например 12:30."
        )
        return VOTER_SLOT_END

    slot_date: date = context.user_data.get('voter_slot_date')
    start_time: time = context.user_data.get('voter_slot_start')
    end_time: time = parsed_time
    voter_id = context.user_data.get('voter_user_id')
    competition_id = context.user_data.get('voter_competition_id')

    # Простая валидация: конец после начала
    if start_time and end_time <= start_time:
        await update.message.reply_text(
            "Время окончания должно быть позже времени начала. Попробуйте снова указать время окончания."
        )
        return VOTER_SLOT_END

    await create_voter_time_slot(
        competition_id=competition_id,
        voter_id=voter_id,
        slot_date=slot_date,
        start_time=start_time,
        end_time=end_time,
    )

    await update.message.reply_text(get_voter_slot_saved_message())
    # Завершаем сценарий и возвращаем в главное меню
    return await start(update, context)
