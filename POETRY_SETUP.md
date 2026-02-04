# 🚀 Быстрый старт с Poetry

## 1️⃣ Установите Poetry (если не установлен)

### Linux / macOS:
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### Windows (PowerShell):
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Проверьте установку:
```bash
poetry --version
```

---

## 2️⃣ Инициализируйте окружение

### Способ 1: Автоматический скрипт (рекомендуется)

**Linux / macOS:**
```bash
chmod +x setup-poetry.sh
./setup-poetry.sh
```

**Windows:**
```bash
setup-poetry.bat
```

### Способ 2: Вручную

```bash
# Перейдите в корневую папку проекта
cd /path/to/tg-bot

# Установите зависимости
poetry install --with dev
```

---

## 3️⃣ Активируйте окружение

### Способ 1: Оболочка Poetry
```bash
poetry shell
# Теперь вы в виртуальном окружении
python --version  # Должно показать Python 3.10+
```

### Способ 2: Запуск команд без активации
```bash
poetry run python manage.py runserver
poetry run pytest
poetry run black .
```

### Выход из окружения:
```bash
exit  # Если использовали "poetry shell"
```

---

## 4️⃣ Проверьте готовность

```bash
# В окружении Poetry:
poetry run python manage.py migrate
poetry run python manage.py runserver

# Или если активирован shell:
python manage.py migrate
python manage.py runserver
```

---

## 📂 Что было создано

| Файл | Описание |
|------|---------|
| `pyproject.toml` | Конфигурация Poetry с зависимостями |
| `Poetry.md` | Полная документация Poetry |
| `setup-poetry.sh` | Скрипт инициализации для Linux/macOS |
| `setup-poetry.bat` | Скрипт инициализации для Windows |
| `.gitignore` | Git правила для Poetry и Django |

---

## 💡 Основные команды

### Управление зависимостями
```bash
# Добавить зависимость
poetry add requests

# Добавить dev зависимость
poetry add --group dev pytest-cov

# Удалить зависимость
poetry remove requests

# Обновить все зависимости
poetry update
```

### Разработка
```bash
# Форматирование кода
poetry run black .

# Проверка стиля
poetry run flake8 .

# Сортировка импортов
poetry run isort .

# Type checking
poetry run mypy backend

# Тесты
poetry run pytest
```

### Django
```bash
# Миграции
poetry run python manage.py migrate

# Создать суперпользователя
poetry run python manage.py createsuperuser

# Запустить сервер
poetry run python manage.py runserver

# Собрать статику
poetry run python manage.py collectstatic
```

---

## 🐳 С Docker

Poetry уже интегрирован в docker-compose.yml:

```bash
# Установить зависимости в контейнере
docker-compose exec backend poetry install

# Запустить миграции
docker-compose exec backend poetry run python manage.py migrate

# Запустить тесты
docker-compose exec backend poetry run pytest
```

---

## ❓ Часто возникающие проблемы

### Poetry не находится в PATH
```bash
# Добавьте в ~/.bashrc или ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

### Нужен requirements.txt для совместимости
```bash
poetry export -f requirements.txt --output requirements.txt
```

### Изменить версию Python
```bash
# Посмотреть доступные версии
poetry env list

# Использовать конкретную версию
poetry env use /usr/bin/python3.11

# Пересоздать окружение
poetry env remove
poetry install
```

### IDE не видит интерпретатор
Укажите путь к интерпретатору:
```bash
poetry env info --path
# Результат: /path/to/.venv
# Используйте: /path/to/.venv/bin/python (Linux/macOS)
# Или: \path\to\.venv\Scripts\python.exe (Windows)
```

---

## 📚 Дополнительные ресурсы

- 📖 [Poetry.md](./Poetry.md) - Полная документация
- 🔗 [Официальная документация Poetry](https://python-poetry.org/docs/)
- 🐍 [Python Poetry на PyPI](https://pypi.org/project/poetry/)

---

## ✅ Готов к работе!

После выполнения этих шагов ваше окружение полностью готово к разработке.

**Следующие шаги:**
1. Активируйте окружение: `poetry shell`
2. Запустите миграции: `python manage.py migrate`
3. Запустите сервер: `python manage.py runserver`
4. Начните разработку! 🚀

---

**Последнее обновление:** февраль 2026
**Проверено на:** Poetry 1.7.0+, Python 3.10+