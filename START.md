# Инструкция по запуску проекта

## Проблема с правами Docker

Если вы видите ошибку `PermissionError: Operation not permitted` при запуске `docker-compose`, нужно исправить права доступа.

### Решение 1: Добавить пользователя в группу docker

```bash
sudo usermod -aG docker $USER
# Затем выйдите и войдите снова, или выполните:
newgrp docker
```

### Решение 2: Запустить с sudo

```bash
sudo docker-compose up -d --build
```

## Запуск через Docker Compose (рекомендуется)

1. Убедитесь, что `.env` файл содержит `TELEGRAM_TOKEN`:
   ```bash
   cat .env
   ```

2. Запустите все сервисы:
   ```bash
   docker-compose up -d --build
   ```

3. Проверьте статус:
   ```bash
   docker-compose ps
   docker-compose logs -f bot
   ```

4. API будет доступно на `http://localhost:4000`
5. Бот запустится автоматически в отдельном контейнере

## Локальный запуск (без Docker)

### Требования:
- Python 3.10+
- PostgreSQL (должна быть запущена и доступна)
- Установленные зависимости

### Шаги:

1. Установите зависимости:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate  # или .venv\Scripts\activate на Windows
   pip install -r requirements.txt
   ```

2. Настройте переменные окружения:
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings
   export DB_NAME=tg_bot
   export DB_USER=postgres
   export DB_PASSWORD=postgres
   export DB_HOST=localhost
   export DB_PORT=5432
   export TELEGRAM_TOKEN=ваш_токен_из_.env
   export ADMIN_TOKEN=changeme
   ```

3. Примените миграции:
   ```bash
   python manage.py migrate
   ```

4. Запустите Django API (в одном терминале):
   ```bash
   python manage.py runserver 0.0.0.0:4000
   ```

5. Запустите бота (в другом терминале):
   ```bash
   python -c "
   import os, django
   os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
   django.setup()
   from telegram.ext import Application
   from apps.bot import setup_bot_handlers
   token = os.environ.get('TELEGRAM_TOKEN')
   if not token:
       raise SystemExit('TELEGRAM_TOKEN not set')
   app = Application.builder().token(token).build()
   setup_bot_handlers(app)
   print('Bot starting (polling)...')
   app.run_polling()
   "
   ```

## Проверка работы

1. Откройте Telegram и найдите вашего бота
2. Отправьте команду `/start`
3. Проверьте API: `curl http://localhost:4000/api/users/ -H "X-Admin-Token: changeme"`

## Остановка

Если запущено через Docker:
```bash
docker-compose down
```

Если запущено локально:
- Нажмите `Ctrl+C` в обоих терминалах
