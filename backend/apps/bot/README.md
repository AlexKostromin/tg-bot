# Архитектура Telegram-бота

Проект разделён на модули для лучшей организации и поддержки кода.

## Структура

```
bot/
├── __init__.py              # Точка входа (setup_bot_handlers)
├── states.py                 # Константы состояний ConversationHandler
├── constants.py              # Роли, паттерны callback'ов, метки
├── keyboards.py              # Функции создания клавиатур
├── messages.py               # Текстовые сообщения бота
├── handlers/                 # Обработчики, сгруппированные по фичам
│   ├── start.py             # /start, главное меню
│   ├── contact.py           # Связь с командой USN
│   ├── registration.py      # Регистрация на соревнования
│   └── profile.py           # Редактирование профиля
└── utils/                    # Утилиты
    ├── db.py                 # Обёртки для Django ORM (sync_to_async)
    └── email.py              # Отправка email
```

## Модули

### `states.py`
Определяет все состояния для `ConversationHandler`. Значения должны быть уникальными.

### `constants.py`
- Роли пользователей (`ROLE_PLAYER`, `ROLE_VOTER`, и т.д.)
- Метки ролей (`ROLE_LABELS`)
- Паттерны для callback'ов (`PATTERN_COMPETITION`, `PATTERN_ROLE`, и т.д.)

### `keyboards.py`
Функции создания inline-клавиатур:
- `get_main_menu_keyboard()` - главное меню
- `get_competitions_keyboard(competitions)` - выбор соревнования
- `get_roles_keyboard()` - выбор роли
- `get_confirmation_keyboard()` - подтверждение данных
- `get_edit_fields_keyboard()` - выбор поля для редактирования
- и т.д.

### `messages.py`
Функции возвращающие текстовые сообщения бота:
- `get_welcome_message()` - приветствие
- `get_contact_prompt()` - запрос сообщения для связи
- `get_user_confirmation_message(user, role)` - данные для подтверждения
- и т.д.

### `handlers/`
Обработчики событий, сгруппированные по функциональности:

#### `start.py`
- `start()` - команда `/start`, показывает главное меню
- `button_start()` - обработка кнопок главного меню

#### `contact.py`
- `contact_message_handler()` - показывает форму для связи
- `contact_message()` - обрабатывает отправленное сообщение

#### `registration.py`
- `show_competitions()` - показывает список соревнований
- `select_competition()` - обработка выбора соревнования
- `show_roles()` - показывает доступные роли
- `select_role()` - обработка выбора роли
- `confirm_existing_user()` - показывает данные существующего пользователя
- `confirm_choice()` - обработка подтверждения/отклонения данных
- `register_new_user_start()` - начало регистрации нового пользователя
- `new_user_*()` - обработчики шагов регистрации нового пользователя
- `finalize_new_user()` - завершение регистрации

#### `profile.py`
- `show_edit_options()` - показывает список полей для редактирования
- `edit_field()` - обработка выбора поля
- `edit_input()` - обработка ввода нового значения
- `more_edits()` - обработка вопроса о дополнительных правках

### `utils/`

#### `db.py`
Обёртки для работы с Django ORM через `sync_to_async`:
- `get_or_create_user()` - получение/создание пользователя
- `get_competitions()` - список соревнований
- `get_competition_by_id()` - соревнование по ID
- `get_user_by_telegram_id()` - пользователь по Telegram ID
- `add_user_to_competition()` - добавление пользователя в соревнование
- `update_or_create_new_user()` - обновление данных пользователя
- `create_profile_log()` - логирование изменений профиля
- `update_user_fields()` - обновление полей пользователя

#### `email.py`
- `send_contact_email()` - отправка email через Django

## Использование

Точка входа - функция `setup_bot_handlers()` в `__init__.py`:

```python
from apps.bot import setup_bot_handlers

app = Application.builder().token(token).build()
setup_bot_handlers(app)
app.run_polling()
```

## Преимущества архитектуры

1. **Разделение по фичам** - каждый handler отвечает за свою область
2. **Переиспользование** - keyboards, messages, utils используются везде
3. **Легко расширять** - добавление новой фичи = новый handler
4. **Удобно тестировать** - изолированные модули
5. **Читаемость** - понятная структура, легко найти нужный код

## Добавление новой фичи

1. Создайте новый файл в `handlers/` (например, `handlers/notifications.py`)
2. Добавьте обработчики функций
3. Импортируйте их в `__init__.py`
4. Добавьте состояния в `states.py` (если нужны новые)
5. Добавьте обработчики в `ConversationHandler.states` в `setup_bot_handlers()`
