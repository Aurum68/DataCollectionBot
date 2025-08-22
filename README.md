# Data Collection Bot
Асинхронный Python-проект для сбора пользовательских данных через Telegram-бота, их сохранения в MySQL и экспорта/бэкапа файлов на Яндекс.Диск.

## Возможности
- Асинхронный Telegram-бот для сбора ответов
- Хранение пользователей и ответов в MySQL
- Роли пользователей (в т.ч. администратор через инвайт-ссылку)
- Экспорт данных в Excel
- Синхронизация файлов с Яндекс.Диском
- Работа через Docker и Docker Compose

## Применяемые технологии
|Технология|Описание|
|-|-|
|Python 3.12+|Язык программирования|
|aiogram/telethon|Telegram-бот|
|aiomysql|Асинхронная работа с MySQL|
|alembic|Миграции MySQL|
|yadisk|Работа с Яндекс.Диском по API|
|openpyxl|Работа с Excel|
|redis|Кеш/очередь сообщений|
|Docker, Docker Compose|Изоляция и управление сервисами|

## Быстрый старт
1. Клонируй репозиторий
  git clone https://github.com/Aurum68/DataCollectionBot.git

  cd DataCollectionBot
3. Заполни переменные окружения
  - Создай .env:
    ```
      TELEGRAM_TOKEN=телеграм_токен
      TELEGRAM_BOT_USERNAME=имя_бота
      MYSQL_USERNAME=имя_пользователя_бд
      MYSQL_ROOT_PASSWORD=пароль_бд
      MYSQL_HOST=mysql
      MYSQL_PORT=порт_бд
      MYSQL_DATABASE=имя_бд
      ADMIN_TELEGRAM_ID=тг_ids (если несколько, то через запятую - 123,654)
      ADMIN_USERNAME=тг_юзернейм
      REDIS_HOST=redis
      REDIS_PORT=редис_порт
      TZ=Europe/Kaliningrad
      YANDEX_TOKEN=токен_яндекс_с_доступом_к_диску
    ```
3. Запусти всё через Docker Compose
```
  docker-compose up --build
```
  **Бот автоматически создаст необходимые файлы и структуру БД, выполнит миграции.**
4. Проверь работу бота
  - Бот работает в Telegram по токену из .env
  - Данные пользователей хранятся в базе MySQL (контейнер mysql)
  - Все пользовательские .xlsx файлы сохраняются локально в ./data и на Яндекс.Диске
  - Файл приглашения администратора: admin_invite.txt в корне проекта
5. docker-compose.yml ключевые сервисы
```
  services:
  init:
    build: .
    volumes:
      - ./data:/app/data
      - ./scripts/create_data_file.py:/app/scripts/create_data_file.py
    working_dir: /app
    command: python ./scripts/create_data_file.py

  mysql:
    image: mysql:8.0
    env_file:
      - .env
    ports:
      - "3306:3306" # Должно совпадать с MYSQL_PORT из .env

  migrations:
    build: .
    depends_on:
      - mysql
    command: alembic upgrade head
    env_file:
      - .env
    volumes:
      - .:/app

  redis:
    image: redis:latest
    ports:
      - "6379:6379" # Должно совпадать с REDIS_PORT из .env

  bot:
    build: .
    depends_on:
      init:
        condition: service_completed_successfully
      mysql:
        condition: service_started
      migrations:
        condition: service_completed_successfully
      redis:
        condition: service_started
    env_file:
      - .env
    volumes:
      - ./data/parameters.xlsx:/app/data/parameters.xlsx
      - ./data/data.xlsx:/app/data/data.xlsx
      - ./.env:/app/.env
    command: ["sh", "-c", "sleep 10 && python src/data_collection_bot/main.py"]
  ```
  
## Особенности и советы
- После первого запуска бот сам создаёт инвайт для администратора (admin_invite.txt)
- Роли пользователей можно изменять через API/бота (через администратора)
- При необходимости вручную инициировать миграции — воспользуйся сервисом migrations
- Для обновления проекта:
    1. git pull
    2. docker-compose up --build
- Для изменения времени отправки сообщений:
    1. Откройте src/data_collection_bot/config.py
    2. Измените параметры HOUR и MINUTE

## Обратная связь
Если есть вопросы/баги — создавай issue на GitHub или пиши @tonledov в Telegram.

# Лицензия
MIT
