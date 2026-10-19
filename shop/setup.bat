@echo off
chcp 65001 >nul
title Установка и запуск проекта BRAT

cd /d "%~dp0"

echo =========================================
echo 1. Установка библиотек для Django (Backend)
echo =========================================

if not exist ..\.venv (
    echo Создание виртуального окружения .venv в родительской папке...
    python -m venv ..\.venv
) else (
    echo Виртуальное окружение .venv уже существует.
)

echo Активация .venv...
call ..\.venv\Scripts\activate

echo Установка библиотек из requirements.txt...
pip install -r requirements.txt
pip install django-cors-headers djangorestframework djangorestframework-simplejwt rapidfuzz

echo.
echo =========================================
echo 2. Настройка базы данных (миграции)...
echo =========================================
python manage.py migrate

echo.
echo =========================================
echo 3. Установка библиотек для Vue (Frontend)
echo =========================================
if exist frontend (
    cd frontend
    echo Установка npm-пакетов...
    call npm install
    cd ..
) else (
    echo [ОШИБКА] Папка frontend не найдена!
)

echo.
echo =========================================
echo 4. АВТОМАТИЧЕСКИЙ ЗАПУСК СЕРВЕРОВ
echo =========================================

start "Django Server" cmd /k "..\.venv\Scripts\activate && python manage.py runserver"

start "Vue Server" cmd /k "cd frontend && npm run dev"

echo.
echo =========================================
echo Ожидание запуска серверов (5 секунд)...
echo =========================================
timeout /t 5 >nul

echo.
echo Открываем сайт в браузере...
start http://localhost:5173/

echo.
echo =========================================
echo ГОТОВО! Проект запущен, сайт открыт в браузере.
echo =========================================

timeout /t 3 >nul
exit