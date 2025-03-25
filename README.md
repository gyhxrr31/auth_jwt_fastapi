# FastAPI Auth System
### Описание:
Данная система реализует регистрацию и авторизацию пользователей с использованием FastAPI, SQLModel, Redis, PostgreSQL и Docker. Авторизация выполняется с помощью JWT-токенов (AuthX).

*В будущем планируется добавить так же поддержку миграций в БД с помощью Alembic*

**Подготовка к запуску**

Создайте .env файл с следующими строками: 
```.dotenv
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
POSTGRES_DB=
JWT_SECRET_KEY=
REDIS_PASSWORD=
```
Заполните их необходимыми данными (порт, хост и т.п)

**Запуск с помощью docker**

```bash
docker compose build
```
```bash
docker compose up
```

