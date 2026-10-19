@echo off
chcp 65001 >nul
title Установка проекта BRAT

echo =========================================
echo Установка библиотек для Django (Backend)
echo =========================================

if not exist venv (
    echo Создание виртуального окружения...
    python -m venv venv
) else (
    echo Виртуальное окружение уже существует.
)

echo Активация виртуального окружения...
call venv\Scripts\activate

echo Установка библиотек из requirements.txt...
pip install -r requirements.txt

pip install rapidfuzz

echo.
echo =========================================
echo Настройка базы данных (миграции)...
echo =========================================
python manage.py migrate

echo.
echo =========================================
echo Установка библиотек для Vue (Frontend)
echo =========================================
cd frontend
echo Установка npm-пакетов (это может занять пару минут)...
call npm install
cd ..

echo.
echo =========================================
echo ГОТОВО! Все библиотеки установлены.
echo =========================================
echo.
echo Чтобы запустить проект, откройте ДВА терминала:
echo.
echo Терминал 1 (Бэкенд):
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Терминал 2 (Фронтенд):
echo   cd frontend
echo   npm run dev
echo =========================================
pause