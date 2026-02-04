# TG Bot (Python/Django)

Проект состоит из:
- **Django API** (DRF) в `backend/` (порт **4000**)
- **Telegram-бота** (polling) в отдельном контейнере `bot` (код в `backend/apps/bot.py`)
- **PostgreSQL** в Docker Compose

## Запуск через Docker Compose (рекомендуется)

1) Создайте переменные окружения (можно в корневом `.env` рядом с `docker-compose.yml`):

```
TELEGRAM_TOKEN=123456:ABCDEF...
ADMIN_TOKEN=changeme
```

2) Поднимите сервисы:

```bash
docker-compose up -d --build
```

API будет доступно на `http://localhost:4000`.

## API

Все API-роуты имеют префикс `/api`:
- `GET /api/users/` — список пользователей (**нужен заголовок** `X-Admin-Token: <ADMIN_TOKEN>`)
- `POST /api/notify/` — рассылка (email часть работает, Telegram-канал требует отдельной интеграции)
- `/api/competitions/` — CRUD соревнований (тоже через `X-Admin-Token`)

## Локальный запуск без Docker (опционально)

Postgres поднимите как удобно, затем:

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=config.settings
export DB_NAME=tg_bot DB_USER=postgres DB_PASSWORD=postgres DB_HOST=127.0.0.1 DB_PORT=5432
export TELEGRAM_TOKEN="..."
export ADMIN_TOKEN="..."

python manage.py migrate
python manage.py runserver 0.0.0.0:4000
```

Бот можно запустить отдельным процессом (пример команды — в `docker-compose.yml`, сервис `bot`).
# tg-bot
