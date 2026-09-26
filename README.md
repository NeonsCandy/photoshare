# PhotoShare API

REST API сервіс для обміну фотографіями, розроблений на базі FastAPI. Проєкт підтримує завантаження світлин у хмарне сховище Cloudinary, управління тегами, коментарями, систему ролей та генерацію QR-кодів.

## Технологічний стек проєкту
- **Фреймворк:** FastAPI
- **База даних:** PostgreSQL + SQLAlchemy Async + Alembic
- **Кешування та Rate Limiting:** Redis + FastAPILimiter
- **Хмарне сховище:** Cloudinary
- **Автентифікація:** JWT, Passlib 
- **Контейнеризація:** Docker, Docker Compose

## Запуск проєкту локально (Docker)

1. Клонуйте репозиторій:
   ```bash
   git clone https://github.com/NeonsCandy/photoshare.git
   cd photoshare
