# 2026-VK-EDU-Web-11-Nesterov-G
## CrowdHelp

Содержится django проект с view страниц и настроенной маршрутизацией. Для генерации html применена шаблонизация

Для запуска из корневой папки проекта вызвать команду docker-compose up --build

Cоздать миграции командой docker compose exec web python manage.py makemigrations

Выполнить миграции командой docker compose exec web python manage.py migrate

Для заполнения БД использовать docker compose exec web python manage.py fill_db --ratio <num>

Сайт находится по адресу http://127.0.0.1:8000/
