"""
Текстовые сообщения бота.
"""
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from apps.users.models import User

from .constants import ROLE_LABELS


class BotMessages:
    """Класс для управления текстовыми сообщениями бота."""

    # Простые сообщения
    WELCOME = "Добро пожаловать! 👋\n\nВыберите действие:"
    CONTACT_PROMPT = "📞 Свяжитесь с командой USN\n\nНапишите ваше сообщение:"
    CONTACT_SUCCESS = (
        "Спасибо за ваше сообщение! 📧\n"
        "Команда USN свяжется с вами в ближайшее время."
    )
    NO_COMPETITIONS = (
        "❌ Сейчас нет активных соревнований для регистрации.\n\n"
        "Если у вас остались вопросы - свяжитесь с командой USN"
    )
    COMPETITION_SELECTION = "⚽ Выберите соревнование - будем рады видеть вас среди участников!"
    ROLE_SELECTION = "В какой роли вы хотите присоединиться?"
    EDIT_PROMPT = "Какие данные вы хотите изменить?"
    FIELD_UPDATED = "Данные обновлены! 📝\n\nНужно внести ещё изменения?"
    CANCEL = "Операция отменена."
    NEW_USER_NAME_PROMPT = "Введите ваше имя в ответ на это сообщение:"
    NEW_USER_SURNAME_PROMPT = "Введите вашу фамилию:"
    NEW_USER_PHONE_PROMPT = (
        "📱 Укажите ваш телефон.\n\n"
        "Нажмите кнопку ниже, чтобы поделиться контактом, "
        "или введите номер телефона вручную."
    )
    NEW_USER_EMAIL_PROMPT = "Укажите ваш email:"
    NEW_USER_BIRTH_DATE_PROMPT = "Укажите вашу дату рождения в формате ГГГГ-ММ-ДД (например, 2010-05-23)."
    NEW_USER_COUNTRY_PROMPT = "Расскажите в какой стране вы живете:"
    NEW_USER_CITY_PROMPT = "Уточните город вашего проживания:"
    NEW_USER_SCHOOL_PROMPT = "Укажите Школу/Клуб, которые вы представляете:"
    NEW_USER_CHANNEL_NAME_PROMPT = (
        "Если у вас есть Telegram-канал, укажите его @username или ссылку.\n"
        "Если нет — напишите «нет»."
    )
    CERTIFICATE_QUESTION = "Регистрация на роль Player/Voter?"
    CERTIFICATE_NAME_PROMPT = "Напишите латиницей Имя и Фамилию для сертификата:"
    COMPANY_PROMPT = "Расскажите в какой компании вы работаете:"
    POSITION_PROMPT = "Уточните вашу должность:"
    IMPORTANT_INFO_PROMPT = "Подскажите, как вас представить на соревнованиях?"
    VOTER_SLOT_DATE_PROMPT = (
        "Теперь выберите, в какой день вы готовы судить.\n"
        "Укажите дату в формате ГГГГ-ММ-ДД (например, 2026-03-15)."
    )
    VOTER_SLOT_START_PROMPT = "Укажите время начала слота в формате ЧЧ:ММ (например, 10:00)."
    VOTER_SLOT_END_PROMPT = "Укажите время окончания слота в формате ЧЧ:ММ (например, 12:30)."
    VOTER_SLOT_SAVED = (
        "Спасибо! Ваш временной слот для судейства сохранён. ✅\n\n"
        "Если потребуется изменить время, свяжитесь с организаторами."
    )

    FIELD_PROMPTS: Dict[str, str] = {
        'name': "Введите ваше имя и фамилию:",
        'phone': "Введите ваш телефон:",
        'email': "Введите ваш email:",
        'city': "Введите ваш город:",
        'school': "Введите школу/клуб:",
        'certificate': "Введите имя и фамилию для сертификата (латиницей):",
        'important': "Как вас представить на соревнованиях?"
    }

    # Методы для сообщений с параметрами
    @staticmethod
    def welcome() -> str:
        """Приветственное сообщение главного меню."""
        return BotMessages.WELCOME

    @staticmethod
    def contact_prompt() -> str:
        """Запрос сообщения для связи с командой USN."""
        return BotMessages.CONTACT_PROMPT

    @staticmethod
    def contact_success() -> str:
        """Подтверждение отправки сообщения."""
        return BotMessages.CONTACT_SUCCESS

    @staticmethod
    def no_competitions() -> str:
        """Сообщение об отсутствии активных соревнований."""
        return BotMessages.NO_COMPETITIONS

    @staticmethod
    def competition_selection() -> str:
        """Сообщение при выборе соревнования."""
        return BotMessages.COMPETITION_SELECTION

    @staticmethod
    def role_selection() -> str:
        """Сообщение при выборе роли."""
        return BotMessages.ROLE_SELECTION

    @staticmethod
    def user_confirmation(user: "User", role: str) -> str:
        """Сообщение с подтверждением данных пользователя."""
        cert_info = f"Имя и фамилия для сертификата: {user.certificate_name or '—'}"
        if role not in ['player', 'voter']:
            cert_info = ""

        lines = [
            f"Добрый день, {user.first_name} {user.last_name}!",
            "Пожалуйста, проверьте ваши данные для регистрации:",
            f"Имя пользователя Telegram: @{user.username or '—'}",
            f"Телефон: {user.phone or '—'}",
            f"Email: {user.email or '—'}",
            f"Страна: {user.country or '—'}",
            f"Город: {user.city or '—'}",
            f"Клуб/школа: {user.school or '—'}",
        ]

        if cert_info:
            lines.append(cert_info)

        lines.extend([
            f"Компания: {user.company or '—'}",
            f"Должность: {user.position or '—'}",
            f"Как вас представить на соревнованиях: {user.important_info or '—'}",
        ])

        return "\n".join(lines)

    @staticmethod
    def registration_success(role: str, comp_name: str) -> str:
        """Сообщение об успешной регистрации."""
        role_label = ROLE_LABELS.get(role, role)
        return f"✅ Отлично! Вы зарегистрированы как {role_label} на {comp_name}."

    @staticmethod
    def new_user_registration_success(user: "User", role: str, comp_name: str) -> str:
        """Сообщение об успешной регистрации нового пользователя."""
        role_label = ROLE_LABELS.get(role, role)
        return (
            f"✅ Отлично! Вы зарегистрированы как {role_label} на {comp_name}.\n\n"
            f"Ваши данные:\n"
            f"Имя: {user.first_name} {user.last_name}\n"
            f"Телефон: {user.phone}\n"
            f"Email: {user.email}\n"
            f"Страна: {user.country}\n"
            f"Город: {user.city}"
        )

    @staticmethod
    def edit_prompt() -> str:
        """Запрос на выбор поля для редактирования."""
        return BotMessages.EDIT_PROMPT

    @staticmethod
    def field_prompts() -> dict:
        """Промпты для редактирования полей."""
        return BotMessages.FIELD_PROMPTS

    @staticmethod
    def field_updated() -> str:
        """Сообщение об обновлении поля."""
        return BotMessages.FIELD_UPDATED

    @staticmethod
    def cancel() -> str:
        """Сообщение об отмене операции."""
        return BotMessages.CANCEL

    @staticmethod
    def new_user_name_prompt() -> str:
        """Запрос имени нового пользователя."""
        return BotMessages.NEW_USER_NAME_PROMPT

    @staticmethod
    def new_user_surname_prompt() -> str:
        """Запрос фамилии нового пользователя."""
        return BotMessages.NEW_USER_SURNAME_PROMPT

    @staticmethod
    def new_user_phone_prompt() -> str:
        """Запрос телефона нового пользователя."""
        return BotMessages.NEW_USER_PHONE_PROMPT

    @staticmethod
    def new_user_email_prompt() -> str:
        """Запрос email нового пользователя."""
        return BotMessages.NEW_USER_EMAIL_PROMPT

    @staticmethod
    def new_user_birth_date_prompt() -> str:
        """Запрос даты рождения нового пользователя."""
        return BotMessages.NEW_USER_BIRTH_DATE_PROMPT

    @staticmethod
    def new_user_country_prompt() -> str:
        """Запрос страны нового пользователя."""
        return BotMessages.NEW_USER_COUNTRY_PROMPT

    @staticmethod
    def new_user_city_prompt() -> str:
        """Запрос города нового пользователя."""
        return BotMessages.NEW_USER_CITY_PROMPT

    @staticmethod
    def new_user_school_prompt() -> str:
        """Запрос школы/клуба нового пользователя."""
        return BotMessages.NEW_USER_SCHOOL_PROMPT

    @staticmethod
    def new_user_channel_name_prompt() -> str:
        """Запрос канала пользователя."""
        return BotMessages.NEW_USER_CHANNEL_NAME_PROMPT

    @staticmethod
    def certificate_question() -> str:
        """Вопрос о необходимости сертификата."""
        return BotMessages.CERTIFICATE_QUESTION

    @staticmethod
    def certificate_name_prompt() -> str:
        """Запрос имени для сертификата."""
        return BotMessages.CERTIFICATE_NAME_PROMPT

    @staticmethod
    def company_prompt() -> str:
        """Запрос компании."""
        return BotMessages.COMPANY_PROMPT

    @staticmethod
    def position_prompt() -> str:
        """Запрос должности."""
        return BotMessages.POSITION_PROMPT

    @staticmethod
    def important_info_prompt() -> str:
        """Запрос важной информации."""
        return BotMessages.IMPORTANT_INFO_PROMPT

    @staticmethod
    def voter_slot_date_prompt() -> str:
        """Запрос даты для слота судьи."""
        return BotMessages.VOTER_SLOT_DATE_PROMPT

    @staticmethod
    def voter_slot_start_prompt() -> str:
        """Запрос времени начала слота судьи."""
        return BotMessages.VOTER_SLOT_START_PROMPT

    @staticmethod
    def voter_slot_end_prompt() -> str:
        """Запрос времени окончания слота судьи."""
        return BotMessages.VOTER_SLOT_END_PROMPT

    @staticmethod
    def voter_slot_saved() -> str:
        """Сообщение о сохранении слота судьи."""
        return BotMessages.VOTER_SLOT_SAVED