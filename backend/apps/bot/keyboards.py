"""
Функции создания клавиатур для бота.
"""
from typing import TYPE_CHECKING, List, Optional, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .constants import AVAILABLE_ROLES

if TYPE_CHECKING:
    from apps.competitions.models import Competition


class KeyboardBuilder:
    """Класс для управления созданием клавиатур бота."""

    def __init__(self) -> None:
        """Инициализировать пустую клавиатуру."""
        self.keyboard: List[List[InlineKeyboardButton]] = []

    def add_button(self, text: str, callback_data: str) -> "KeyboardBuilder":
        """Добавить кнопку в отдельный ряд."""
        self.keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        return self

    def add_button_row(self, buttons: List[Tuple[str, str]]) -> "KeyboardBuilder":
        """Добавить ряд кнопок. buttons - список (текст, callback_data)."""
        row = [InlineKeyboardButton(text, callback_data=callback_data) for text, callback_data in buttons]
        self.keyboard.append(row)
        return self

    def add_cancel_button(self, text: str = "❌ Отмена") -> "KeyboardBuilder":
        """Добавить кнопку отмены."""
        return self.add_button(text, 'cancel')

    def add_yes_no_buttons(self, yes_callback: str = "yes", no_callback: str = "no",
                          yes_text: str = "✅ Да", no_text: str = "❌ Нет") -> "KeyboardBuilder":
        """Добавить кнопки Yes/No."""
        return self.add_button_row([
            (yes_text, yes_callback),
            (no_text, no_callback),
        ])

    def build(self) -> InlineKeyboardMarkup:
        """Построить и вернуть InlineKeyboardMarkup."""
        return InlineKeyboardMarkup(self.keyboard)

    def clear(self) -> None:
        """Очистить клавиатуру."""
        self.keyboard = []

    # ============ Предсборные клавиатуры ============

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Главное меню бота."""
        return (KeyboardBuilder()
                .add_button("💬 Связаться с командой USN", 'contact_usn')
                .add_button("⚽ Зарегистрироваться на соревнования", 'register_competition')
                .build())

    @staticmethod
    def competitions(competitions: List["Competition"]) -> InlineKeyboardMarkup:
        """Клавиатура выбора соревнования."""
        builder = KeyboardBuilder()
        for comp in competitions:
            builder.add_button(comp.name, f'comp_{comp.id}')
        builder.add_cancel_button()
        return builder.build()

    @staticmethod
    def roles(open_roles: Optional[List[str]] = None) -> InlineKeyboardMarkup:
        """Клавиатура выбора роли. Если передан open_roles, показывает только доступные роли."""
        builder = KeyboardBuilder()
        for role_key, role_name in AVAILABLE_ROLES:
            if open_roles is None or role_key in open_roles:
                builder.add_button(role_name, f'role_{role_key}')
        builder.add_cancel_button()
        return builder.build()

    @staticmethod
    def confirmation() -> InlineKeyboardMarkup:
        """Клавиатура подтверждения данных."""
        return (KeyboardBuilder()
                .add_yes_no_buttons(yes_callback='confirm_yes', no_callback='confirm_no')
                .build())

    @staticmethod
    def edit_fields() -> InlineKeyboardMarkup:
        """Клавиатура выбора поля для редактирования."""
        return (KeyboardBuilder()
                .add_button("Имя и фамилия", 'edit_name')
                .add_button("Телефон", 'edit_phone')
                .add_button("Email", 'edit_email')
                .add_button("Город", 'edit_city')
                .add_button("Клуб/школа", 'edit_school')
                .add_button("Имя и фамилия для сертификата", 'edit_certificate')
                .add_button("Как вас представить на соревнованиях", 'edit_important')
                .add_cancel_button()
                .build())

    @staticmethod
    def more_edits() -> InlineKeyboardMarkup:
        """Клавиатура вопроса о дополнительных правках."""
        return (KeyboardBuilder()
                .add_yes_no_buttons(yes_callback='more_edits_yes', no_callback='more_edits_no')
                .build())

    @staticmethod
    def certificate_choice() -> InlineKeyboardMarkup:
        """Клавиатура выбора необходимости сертификата."""
        return (KeyboardBuilder()
                .add_yes_no_buttons(yes_callback='cert_yes', no_callback='cert_no')
                .build())


# ============ Функции для обратной совместимости ============

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    return KeyboardBuilder.main_menu()


def get_competitions_keyboard(competitions: List["Competition"]) -> InlineKeyboardMarkup:
    """Клавиатура выбора соревнования."""
    return KeyboardBuilder.competitions(competitions)


def get_roles_keyboard(open_roles: Optional[List[str]] = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора роли. Если передан open_roles, показывает только доступные роли."""
    return KeyboardBuilder.roles(open_roles)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения данных."""
    return KeyboardBuilder.confirmation()


def get_edit_fields_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования."""
    return KeyboardBuilder.edit_fields()


def get_more_edits_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура вопроса о дополнительных правках."""
    return KeyboardBuilder.more_edits()


def get_certificate_choice_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора необходимости сертификата."""
    return KeyboardBuilder.certificate_choice()