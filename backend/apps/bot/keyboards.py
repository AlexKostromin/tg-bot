"""
Функции создания клавиатур для бота.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .constants import AVAILABLE_ROLES


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    keyboard = [
        [InlineKeyboardButton("💬 Связаться с командой USN", callback_data='contact_usn')],
        [InlineKeyboardButton("⚽ Зарегистрироваться на соревнования", callback_data='register_competition')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_competitions_keyboard(competitions) -> InlineKeyboardMarkup:
    """Клавиатура выбора соревнования."""
    keyboard = []
    for comp in competitions:
        keyboard.append([InlineKeyboardButton(comp.name, callback_data=f'comp_{comp.id}')])
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='cancel')])
    return InlineKeyboardMarkup(keyboard)


def get_roles_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора роли."""
    keyboard = []
    for role_key, role_name in AVAILABLE_ROLES:
        keyboard.append([InlineKeyboardButton(role_name, callback_data=f'role_{role_key}')])
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='cancel')])
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения данных."""
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data='confirm_yes')],
        [InlineKeyboardButton("❌ Нет", callback_data='confirm_no')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_edit_fields_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования."""
    keyboard = [
        [InlineKeyboardButton("Имя и фамилия", callback_data='edit_name')],
        [InlineKeyboardButton("Телефон", callback_data='edit_phone')],
        [InlineKeyboardButton("Email", callback_data='edit_email')],
        [InlineKeyboardButton("Город", callback_data='edit_city')],
        [InlineKeyboardButton("Клуб/школа", callback_data='edit_school')],
        [InlineKeyboardButton("Имя и фамилия для сертификата", callback_data='edit_certificate')],
        [InlineKeyboardButton("Как вас представить на соревнованиях", callback_data='edit_important')],
        [InlineKeyboardButton("❌ Отмена", callback_data='cancel')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_more_edits_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура вопроса о дополнительных правках."""
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data='more_edits_yes')],
        [InlineKeyboardButton("❌ Нет", callback_data='more_edits_no')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_certificate_choice_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора необходимости сертификата."""
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data='cert_yes')],
        [InlineKeyboardButton("❌ Нет", callback_data='cert_no')]
    ]
    return InlineKeyboardMarkup(keyboard)
