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

###  Запуск Django

1. Примените миграции для настройки базы данных
```bash
    python manage.py makemigrations
    python manage.py migrate
```
1. Создайте суперпользователя для доступа к административной панели
```bash
    python manage.py createsuperuser
```
1. Запуск сервера разработки
```bash
    python manage.py runserver
```
4. Сервер будет доступен по адресу: http://127.0.0.1:8000/api/

### Тестирование API

1. http://127.0.0.1:8000/api/docs
2. http://127.0.0.1:8000/api/redoc

