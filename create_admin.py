#!/usr/bin/env python
"""
Скрипт для создания суперпользователя и демо-данных
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')

django.setup()

from django.contrib.auth.models import User
# from apps.users.models import User as TgUser
from apps.competitions.models import Competition

# Создаём суперпользователя для админ панели
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("✓ Суперпользователь 'admin' создан (пароль: admin)")
else:
    print("✓ Суперпользователь уже существует")

# Демо-данные: создаём тестовое соревнование
if not Competition.objects.exists():
    comp = Competition.objects.create(
        name='Чемпионат по шахматам',
        description='Главное соревнование сезона'
    )
    print(f"✓ Соревнование '{comp.name}' создано")
else:
    print("✓ Соревнования уже существуют")

print("\nАдминистратор готов к использованию!")
print("Логин: admin")
print("Пароль: admin")
print("URL: http://localhost:4000/admin/")
