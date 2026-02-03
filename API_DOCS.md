# API Документация

Автоматическая документация доступна по адресам:

- **Swagger UI**: http://localhost:4000/api/docs/
- **ReDoc**: http://localhost:4000/api/redoc/
- **OpenAPI Schema**: http://localhost:4000/api/schema/

## Примеры использования API

### Требование: X-Admin-Token

Все API endpoints требуют заголовок `X-Admin-Token` для доступа.

По умолчанию: `changeme` (измените в production!)

### 1. Получить список пользователей

```bash
curl -H "X-Admin-Token: changeme" http://localhost:4000/api/users/
```

**Ответ:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "chat_id": "123456789",
      "telegram_id": "123456789",
      "first_name": "Иван",
      "last_name": "Петров",
      "username": "ivan_petrov",
      "email": "ivan@example.com",
      "phone": "+79991234567",
      "role": "player",
      "classic_rating": 2000.5,
      "quick_rating": 1900.0,
      "team_rating": 2100.0,
      "city": "Москва",
      "country": "Россия",
      "school": "Шахматный клуб №1",
      "created_at": "2026-02-03T07:30:00Z"
    }
  ]
}
```

---

### 2. Получить конкретного пользователя

```bash
curl -H "X-Admin-Token: changeme" http://localhost:4000/api/users/1/
```

---

### 3. Получить список соревнований

```bash
curl -H "X-Admin-Token: changeme" http://localhost:4000/api/competitions/
```

**Ответ:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Чемпионат по шахматам",
      "description": "Главное соревнование сезона",
      "entry_open_player": true,
      "entry_open_voter": true,
      "entry_open_viewer": true,
      "entry_open_adviser": true,
      "arbitrators": [1],
      "voters": [],
      "viewers": [],
      "advisers": [],
      "created_at": "2026-02-03T07:30:00Z"
    }
  ]
}
```

---

### 4. Создать новое соревнование

```bash
curl -X POST -H "X-Admin-Token: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Кубок России",
    "description": "Региональный чемпионат",
    "entry_open_player": true,
    "entry_open_voter": true
  }' \
  http://localhost:4000/api/competitions/
```

---

### 5. Отправить рассылку

```bash
curl -X POST -H "X-Admin-Token: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Сегодня в 18:00 начинается турнир!",
    "subject": "Напоминание о турнире",
    "role": "player",
    "channels": ["tg", "email"]
  }' \
  http://localhost:4000/api/notify/
```

**Ответ:**
```json
{
  "total_users": 5,
  "tg_enqueued": 5,
  "results": [
    {
      "id": 1,
      "chat_id": "123456789",
      "email": "ivan@example.com",
      "ok": true,
      "details": [
        {"channel": "tg", "ok": true, "queued": true},
        {"channel": "email", "ok": true}
      ]
    }
  ]
}
```

---

### 6. Обновить соревнование

```bash
curl -X PUT -H "X-Admin-Token: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Кубок России 2026",
    "description": "Региональный чемпионат с измененным названием",
    "entry_open_player": true
  }' \
  http://localhost:4000/api/competitions/1/
```

---

### 7. Удалить соревнование

```bash
curl -X DELETE -H "X-Admin-Token: changeme" \
  http://localhost:4000/api/competitions/1/
```

---

## Коды ответов

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан
- `204 No Content` - Успешное удаление
- `400 Bad Request` - Неверные параметры
- `401 Unauthorized` - Неверный или отсутствующий токен
- `404 Not Found` - Ресурс не найден
- `405 Method Not Allowed` - Метод не поддерживается

---

## Роли пользователей

- `player` - Игрок
- `voter` - Судья
- `viewer` - Зритель
- `adviser` - Секундант
- `admin` - Администратор

---

## Статусы рассылок

- `pending` - Ожидание отправки
- `sent` - Отправлено
- `failed` - Ошибка отправки
