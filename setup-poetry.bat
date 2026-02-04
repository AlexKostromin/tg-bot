@echo off
REM ############################################################################
REM Скрипт для инициализации Poetry окружения проекта tg-bot (Windows)
REM
REM Использование:
REM   setup-poetry.bat
REM ############################################################################

setlocal enabledelayedexpansion

echo.
echo ========================================
echo 🚀 Инициализация Poetry окружения...
echo ========================================
echo.

REM Проверка установки Poetry
where poetry >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Poetry не установлен!
    echo.
    echo 📦 Пожалуйста, установите Poetry:
    echo    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing^).Content ^| python -
    echo.
    pause
    exit /b 1
)

echo ✅ Poetry найден:
poetry --version
echo.

REM Проверка версии Python
echo 🐍 Проверка Python...
python --version
echo.

REM Установка зависимостей
echo 📥 Установка зависимостей...
poetry install --with dev

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Ошибка при установке зависимостей
    pause
    exit /b 1
)

echo.
echo ✅ Зависимости установлены!
echo.

REM Информация об окружении
echo 📋 Информация об окружении:
poetry env info

echo.
echo ========================================
echo ✨ Готово! Теперь вы можете:
echo ========================================
echo.
echo   1️⃣  Активировать окружение:
echo      poetry shell
echo.
echo   2️⃣  Или запустить команды напрямую:
echo      poetry run python manage.py migrate
echo      poetry run python manage.py runserver
echo.
echo   3️⃣  Запустить тесты:
echo      poetry run pytest
echo.
echo   4️⃣  Запустить линтеры:
echo      poetry run black .
echo      poetry run flake8 .
echo      poetry run mypy backend
echo.
echo 📚 Для подробной информации смотрите Poetry.md
echo.

pause