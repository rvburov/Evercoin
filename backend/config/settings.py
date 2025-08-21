import os
from pathlib import Path
from decouple import config 
from datetime import timedelta

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ приложения, считываемый из переменных окружения
SECRET_KEY = config('SECRET_KEY')

# Режим отладки: включается/выключается через переменные окружения
DEBUG = config('DEBUG', default=False, cast=bool)

# Разрешенные хосты для развертывания проекта
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Доверенные источники для CSRF-токенов
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='').split(',')

# Список приложений Django (встроенные)
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Сторонние приложения, установленные через pip
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_filters',
]

# Локальные приложения проекта (созданные пользователем)
LOCAL_APPS = [
    'api.users',
    'api.operations',
    'api.wallets',
    'api.categories',
]

# Полный список установленных приложений
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

# Список middleware для обработки запросов/ответов
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Корневая конфигурация URL
ROOT_URLCONF = 'config.urls'

# Настройки шаблонов Django
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI-приложение
WSGI_APPLICATION = 'config.wsgi.application'

# Настройки базы данных SQLite
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Язык и часовой пояс проекта
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'

# Включение интернационализации и поддержки часовых зон
USE_I18N = True
USE_TZ = True

# Автоматическое поле первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки для статических файлов
STATIC_URL = '/static/'                               
STATICFILES_DIRS = [BASE_DIR / 'static',]             
STATIC_ROOT = BASE_DIR / 'staticfiles'               

# Настройки для медиа-файлов
MEDIA_URL = '/media/'  
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')          

# Настройки пользовательской модели пользователя
AUTH_USER_MODEL = 'users.CustomUser'

# Настройка аутентификации для Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Настройки для работы с JWT-токенами (опционально)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Настройки документации API
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Evercoin',
    'DESCRIPTION': 'API для Evercoin',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Настройки email 
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Для разработки
EMAIL_HOST = config('EMAIL_HOST')                                 # SMTP-сервер
EMAIL_PORT = config('EMAIL_PORT', cast=int)                       # Порт для SMTP
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)                # Использование SSL
EMAIL_HOST_USER = config('EMAIL_HOST_USER')                       # Логин SMTP
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')               # Пароль SMTP
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER                              # Email отправителя
SERVER_EMAIL = EMAIL_HOST_USER                                    # Email для системных уведомлений
EMAIL_ADMIN = EMAIL_HOST_USER                                     # Email администратора
