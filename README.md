### Клонирования репозитория из GitHub

```bash
git clone https://github.com/rvburov/Evercoin.git
```

### Настройка виртуальное окружения для тестирование

1. Установка
```bash
    python3 -m venv venv          # MacOS и Linux
    python -m venv venv           # Windows
```

2. Запуск
```bash
    source venv/bin/activate      # MacOS и Linux
    source venv/Scripts/activate  # Windows
```

### Настройка и установка приложения

1. Обновление pip
```bash
    python -m pip install --upgrade pip
    pip --version
```

2. Установка пакетов из файла зависимостей
```bash
    pip install -r requirements.txt
```

###  Запуск сервера Django

1. Примените миграции для настройки базы данных
```bash
    python manage.py makemigrations
    python manage.py migrate
```
2. Создайте суперпользователя для доступа к административной панели
```bash
    python manage.py createsuperuser
```
3. Загрузить все статические файлы
```bash
    python manage.py collectstatic
```
4. Запуск сервера разработки
```bash
    python manage.py runserver
```
4. Сервер будет доступен по адресу: http://127.0.0.1:8000/api/

### Тестирование API

1. http://127.0.0.1:8000/api/docs
2. http://127.0.0.1:8000/api/redoc

## 🧪 Тестирование

### Запуск тестов
```bash
# Запуск конкретного файла
pytest api/users/tests.py

# Запуск конкретного класса тестов
pytest api/users/test_views.py::TestUserRegistrationView

# Запуск конкретного теста
pytest api/users/test_views.py::TestUserRegistrationView::test_successful_registration
```

### Структура проекта
```bash
Evercoin/                                        # Корневая директория проекта
│
├── backend/                                     # Backend-часть на Django
│   │
│   ├── config/                                  # Основной конфигурационный модуль Django
│   │   ├── settings.py                          # Настройки проекта (база данных, middleware, installed apps)
│   │   ├── urls.py                              # Корневая конфигурация URL (маршрутизация всего проекта)
│   │   ├── asgi.py                              # ASGI-конфигурация для асинхронных серверов (Daphne)
│   │   └── wsgi.py                              # WSGI-конфигурация для традиционных серверов (Gunicorn)
│   │
│   ├── api                                      # Основное API приложение
│   │    ├── core/                               # Основные данные и утилиты
│   │    │    └── constants/                     # Данные, которые не меняются
│   │    │        ├── colors.py                  # Цвета в HEX/RGB с названиями
│   │    │        ├── currencies.py              # Список валют с кодами, символами и точностью
│   │    │        └── icons.py                   # Доступные иконки с путями к файлам
│   │    │
│   │    ├── users/                              # Приложение авторизации, аутентификации и работа с пользователями
│   │    │    ├── admin.py                       # Админка для пользователей (кастомизация админ-панели)
│   │    │    ├── models.py                      # Кастомная модель пользователя (расширение AbstractUser)
│   │    │    ├── serializers.py                 # Сериализаторы пользователей (DRF сериализаторы)
│   │    │    ├── urls.py                        # URL для работы с пользователями (регистрация, профиль)
│   │    │    ├── views.py                       # View для операций с пользователями (API endpoints)
│   │    │    ├── validators.py                  # Кастомные валидаторы (проверка email, паролей)
│   │    │    └── tests.py                       # Тесты пользовательского функционала
│   │    │
│   │    ├── operations/                         # Приложение финансовых операций
│   │    │    ├── admin.py                       # Админка для операций (фильтры, поиск)
│   │    │    ├── models.py                      # Модели доходов/расходов (сумма, дата, категория)
│   │    │    ├── serializers.py                 # Сериализаторы операций (создание, чтение, обновление)
│   │    │    ├── urls.py                        # URL для операций (CRUD endpoints)
│   │    │    ├── views.py                       # View для операций (логика обработки запросов)
│   │    │    ├── validators.py                  # Валидаторы операций (проверка сумм, дат)
│   │    │    └── tests.py                       # Тесты операций (создание, фильтрация)
│   │    │
│   │    ├── categories/                         # Приложение категорий операций
│   │    │    ├── admin.py                       # Админка категорий (иерархическое отображение)
│   │    │    ├── models.py                      # Модели категорий (название, иконка, цвет)
│   │    │    ├── serializers.py                 # Сериализаторы категорий (вложенные структуры)
│   │    │    ├── urls.py                        # URL для категорий (получение списка)
│   │    │    ├── views.py                       # View для категорий (кеширование)
│   │    │    ├── validators.py                  # Валидаторы категорий (уникальность имен)
│   │    │    └── tests.py                       # Тесты категорий (создание, привязка к операциям)
│   │    │
│   │    ├── wallets/                            # Приложение финансовых счетов
│   │    │    ├── admin.py                       # Админка счетов (статистика по счетам)
│   │    │    ├── models.py                      # Модели счетов (название, баланс, валюта)
│   │    │    ├── serializers.py                 # Сериализаторы счетов (расчет баланса)
│   │    │    ├── urls.py                        # URL для счетов (переводы между счетами)
│   │    │    ├── views.py                       # View для счетов (проверка прав доступа)
│   │    │    ├── validators.py                  # Валидаторы счетов (проверка валюты)
│   │    │    └── tests.py                       # Тесты счетов (пополнение, списание)
│   │    │
│   │    └── notifications/                      # Приложение уведомлений
│   │         ├── admin.py                       # Админка уведомлений (фильтр по статусу)
│   │         ├── models.py                      # Модели уведомлений (прочитано/не прочитано)
│   │         ├── serializers.py                 # Сериализаторы уведомлений (маркировка прочитанных)
│   │         ├── urls.py                        # URL для уведомлений (вебсокеты)
│   │         ├── views.py                       # View для уведомлений (отправка через Celery)
│   │         ├── validators.py                  # Валидаторы уведомлений (проверка шаблонов)
│   │         └── tests.py                       # Тесты уведомлений (триггеры отправки)
│   │
│   ├── static/                                  # Статические данные (collectstatic)
│   │   └── icons                                # SVG/PNG иконки
│   │       ├── categories                       # Иконки для категорий (20x20px)
│   │       └── wallets                          # Иконки для счетов (32x32px)
│   │
│   ├── media/                                   # Динамически загружаемые файлы
│   │   └── avatar                               # Аватарки пользователей (JPG/PNG)
│   │
│   ├── requirements.txt                         # Зависимости проекта (основные пакеты)
│   ├── manage.py                                # Утилита управления Django (миграции, запуск)
│   ├── Dockerfile                               # Конфигурация Docker-образа (Python + зависимости)
│   └── .dockerignore                            # Исключения для Docker-сборки (кеши, логи)
│
├── nginx/                                       # Конфигурация Nginx (проксирование)
│   ├── nginx.conf                               # Основной конфиг Nginx (gzip, ssl)
│   └── Dockerfile                               # Сборка Nginx-образа (оптимизированный)
│
├── .github/workflows/                           # CI/CD автоматизация
│   └── ci-cd.yml                                # Конфигурация GitHub Actions (тесты, деплой)
│
├── docker-compose.yml                           # Конфигурация для разработки (Django + PostgreSQL + Redis)
├── docker-compose.prod.yml                      # Конфигурация для продакшена (Gunicorn + Traefik)
├── .env.example                                 # Пример переменных окружения (SECRET_KEY, DB_URL)
├── .env                                         # Окружение (SECRET_KEY, DB_URL)
├── .gitignore                                   # Игнорируемые файлы Git (venv, .pyc, .env)
└── README.md                                    # Основная документация проекта (установка, настройка)                         
```
