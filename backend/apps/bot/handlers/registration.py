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
    NEW_USER_CERT_ROLE_CONFIRM,
    NEW_USER_IMPORTANT,
    VOTER_SLOT_DATE,
    VOTER_SLOT_START,
    VOTER_SLOT_END,
)
from ..keyboards import (
    get_competitions_keyboard, get_roles_keyboard, get_confirmation_keyboard,
    get_certificate_choice_keyboard, get_phone_keyboard, get_remove_keyboard,
)
from ..messages import BotMessages
from ..utils.db import (
    get_competitions,
    get_competition_by_id,
    get_user_by_telegram_id,
    add_user_to_competition,
    update_or_create_new_user,
    create_voter_time_slot,
    create_registration_request,
    get_open_roles_for_competition,
)
from .start import start
from .profile import show_edit_options


async def show_competitions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available competitions"""
    query = update.callback_query if update.callback_query else None
    
    competitions = await get_competitions()
    
    if not competitions:
        text = BotMessages.no_competitions()
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
    text = BotMessages.competition_selection()
    
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
    """Show available roles for competition (filtered by entry_open flags)"""
    query = update.callback_query if update.callback_query else None

    comp_id = context.user_data.get('competition_id')
    comp = await get_competition_by_id(comp_id)

    open_roles = await get_open_roles_for_competition(comp)

    if not open_roles:
        text = BotMessages.no_competitions()
        if query:
            await query.edit_message_text(text=text)
        else:
            await update.message.reply_text(text)
        return await start(update, context)

    reply_markup = get_roles_keyboard(open_roles=open_roles)
    text = BotMessages.role_selection()

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
    
    text = BotMessages.user_confirmation(user, role)
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
        await create_registration_request(user, comp, role)

        if role == 'voter':
            return await start_voter_timeslot_flow(update, context, user, comp_id)

        text = BotMessages.registration_success(role, comp_name)
        await query.edit_message_text(text=text)

        return await start(update, context)

    else:
        return await show_edit_options(update, context)


# Новые пользователи
async def register_new_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start new user registration"""
    query = update.callback_query
    await query.edit_message_text(text=BotMessages.new_user_name_prompt())
    return NEW_USER_NAME


async def new_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['first_name'] = update.message.text
    await update.message.reply_text(BotMessages.new_user_surname_prompt())
    return NEW_USER_SURNAME


async def new_user_surname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['last_name'] = update.message.text
    reply_markup = get_phone_keyboard()
    await update.message.reply_text(
        BotMessages.new_user_phone_prompt(),
        reply_markup=reply_markup
    )
    return NEW_USER_PHONE


async def new_user_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    import re
    # If user shared contact
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
    # If user clicked "Enter manually"
    elif update.message.text == "✍️ Ввести вручную":
        await update.message.reply_text(
            "Введите ваш номер телефона:",
            reply_markup=get_remove_keyboard()
        )
        return NEW_USER_PHONE
    # User entered phone as text
    else:
        phone = update.message.text.strip()
        # Валидация: минимум 5 цифр
        if not re.search(r'\d', phone) or len(re.sub(r'\D', '', phone)) < 5:
            await update.message.reply_text(
                "❌ Пожалуйста, введите корректный номер телефона.\n"
                "Телефон должен содержать минимум 5 цифр."
            )
            return NEW_USER_PHONE
        context.user_data['phone'] = phone

    # Remove keyboard and move to email
    await update.message.reply_text(
        BotMessages.new_user_email_prompt(),
        reply_markup=get_remove_keyboard()
    )
    return NEW_USER_EMAIL


async def new_user_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    import re
    email = update.message.text.strip()

    # Валидация email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        await update.message.reply_text(
            "❌ Пожалуйста, введите корректный email адрес.\n"
            "Например: example@domain.com"
        )
        return NEW_USER_EMAIL

    context.user_data['email'] = email
    await update.message.reply_text(BotMessages.new_user_country_prompt())
    return NEW_USER_COUNTRY


async def new_user_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['country'] = update.message.text
    await update.message.reply_text(BotMessages.new_user_city_prompt())
    return NEW_USER_CITY


async def new_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['city'] = update.message.text
    await update.message.reply_text(BotMessages.new_user_school_prompt())
    return NEW_USER_SCHOOL


async def new_user_school(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['school'] = update.message.text

    # ALWAYS ask the first Player/Voter question (regardless of role!)
    reply_markup = get_certificate_choice_keyboard()
    await update.message.reply_text(
        BotMessages.certificate_question(),
        reply_markup=reply_markup
    )
    return NEW_USER_CERT_ROLE


async def new_user_cert_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle FIRST Player/Voter question"""
    query = update.callback_query
    await query.answer()

    # Save the first answer
    context.user_data['first_cert_answer'] = query.data  # 'cert_yes' or 'cert_no'

    if query.data == 'cert_yes':
        # If YES - ask for certificate name immediately
        await query.edit_message_text(BotMessages.certificate_name_prompt())
        return NEW_USER_CERT_NAME
    else:
        # If NO - ask for company
        await query.edit_message_text(BotMessages.company_prompt())
        return NEW_USER_COMPANY


async def new_user_cert_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['certificate_name'] = update.message.text
    await update.message.reply_text(BotMessages.company_prompt())
    return NEW_USER_COMPANY


async def new_user_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['company'] = update.message.text
    await update.message.reply_text(BotMessages.position_prompt())
    return NEW_USER_POSITION

async def new_user_cert_name_late(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Request certificate name for users who changed their mind (second NO → second YES)"""
    context.user_data['certificate_name'] = update.message.text
    await update.message.reply_text(BotMessages.important_info_prompt())
    return NEW_USER_IMPORTANT


async def new_user_cert_role_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle SECOND Player/Voter question"""
    query = update.callback_query
    await query.answer()

    first_answer = context.user_data.get('first_cert_answer')  # 'cert_yes' or 'cert_no'
    second_answer = query.data  # 'cert_yes' or 'cert_no'

    # Scenario 1: First YES, Second YES
    if first_answer == 'cert_yes' and second_answer == 'cert_yes':
        # Already has certificate_name, ask for "how to present"
        await query.edit_message_text(BotMessages.important_info_prompt())
        return NEW_USER_IMPORTANT

    # Scenario 2: First YES, Second NO
    elif first_answer == 'cert_yes' and second_answer == 'cert_no':
        # Already has certificate_name, but DON'T ask for important_info
        return await finalize_new_user(update, context)

    # Scenario 3: First NO, Second YES
    elif first_answer == 'cert_no' and second_answer == 'cert_yes':
        # DON'T have certificate_name, ask for it
        await query.edit_message_text(BotMessages.certificate_name_prompt())
        return NEW_USER_CERT_NAME_LATE

    # Scenario 4: First NO, Second NO
    else:
        # Create user without certificate and without important_info
        return await finalize_new_user(update, context)


async def new_user_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['position'] = update.message.text

    # ALWAYS ask the SECOND Player/Voter question (after company/position)
    reply_markup = get_certificate_choice_keyboard()
    await update.message.reply_text(
        BotMessages.certificate_question(),
        reply_markup=reply_markup
    )
    return NEW_USER_CERT_ROLE_CONFIRM


async def new_user_important(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['important_info'] = update.message.text
    return await finalize_new_user(update, context)


async def new_user_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Legacy handler - not used in new flow but kept for backward compatibility"""
    text = update.message.text.strip()
    if text.lower() == 'нет' or text == '-':
        context.user_data['birth_date'] = None
    else:
        try:
            parsed = datetime.strptime(text, "%Y-%m-%d").date()

            # Валидация: дата не в будущем и после 1900 года
            today = date.today()
            if parsed > today:
                await update.message.reply_text(
                    "❌ Дата рождения не может быть в будущем.\n"
                    "Пожалуйста, используйте формат ГГГГ-ММ-ДД, например 2010-05-23."
                )
                return NEW_USER_BIRTH_DATE

            if parsed.year < 1900:
                await update.message.reply_text(
                    "❌ Пожалуйста, введите корректную дату рождения (после 1900 года).\n"
                    "Формат: ГГГГ-ММ-ДД, например 2010-05-23."
                )
                return NEW_USER_BIRTH_DATE

            context.user_data['birth_date'] = parsed
        except ValueError:
            await update.message.reply_text(
                "❌ Не удалось распознать дату. Пожалуйста, используйте формат ГГГГ-ММ-ДД, например 2010-05-23."
            )
            return NEW_USER_BIRTH_DATE

    await update.message.reply_text(BotMessages.new_user_country_prompt())
    return NEW_USER_COUNTRY


async def new_user_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Legacy handler - not used in new flow but kept for backward compatibility"""
    raw = update.message.text.strip()
    if raw.lower() in ('нет', 'no', '-'):
        context.user_data['channel_name'] = None
    else:
        context.user_data['channel_name'] = raw
    await update.message.reply_text(BotMessages.company_prompt())
    return NEW_USER_COMPANY


async def finalize_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create new user and show confirmation (NOT registering to competition yet)"""
    chat_id = context.user_data.get('chat_id')
    telegram_id = context.user_data.get('telegram_id')

    # Create user in DB (but do NOT register to competition yet)
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
        birth_date=None,  # Not requested in new flow
        channel_name=None,  # Not requested in new flow
    )

    # Show user data for confirmation (same as existing users)
    role = context.user_data.get('role')
    text = BotMessages.user_confirmation(user, role)
    reply_markup = get_confirmation_keyboard()

    # Send message based on whether it came from callback or message
    if getattr(update, "callback_query", None):
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

    # Move to CONFIRM_DATA state (same as existing users!)
    return CONFIRM_DATA


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
        await update.callback_query.edit_message_text(BotMessages.voter_slot_date_prompt())
    else:
        await update.message.reply_text(BotMessages.voter_slot_date_prompt())
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
    await update.message.reply_text(BotMessages.voter_slot_start_prompt())
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
    await update.message.reply_text(BotMessages.voter_slot_end_prompt())
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

    await update.message.reply_text(BotMessages.voter_slot_saved())
    # Завершаем сценарий и возвращаем в главное меню
    return await start(update, context)
