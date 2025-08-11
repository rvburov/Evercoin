import os
from pathlib import Path
from decouple import config 

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
    'django.contrib.sites', 
]

# Локальные приложения проекта (созданные пользователем)
LOCAL_APPS = [
    'users',
]

# Сторонние приложения, установленные через pip
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken', 
    'dj_rest_auth',
    'allauth',
    'allauth.account', 
    'allauth.socialaccount', 
    'allauth.socialaccount.providers.google'
    'allauth.socialaccount.providers.yandex'
    'dj_rest_auth.registration',
    'corsheaders',
    'drf_spectacular',
]

# Полный список установленных приложений
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

# Список middleware для обработки запросов/ответов
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

# Настройки базы данных (SQLite по умолчанию, PostgreSQL через переменные окружения)
if config('USE_POSTGRESQL', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB'),
            'USER': config('POSTGRES_USER'),
            'PASSWORD': config('POSTGRES_PASSWORD'),
            'HOST': config('POSTGRES_HOST', default='localhost'),
            'PORT': config('POSTGRES_PORT', default='5432'),
        }
    }
else:
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
STATIC_URL = '/static/'                               # URL для статических файлов
STATICFILES_DIRS = [BASE_DIR / 'static',]             # Директории со статическими файлами
STATIC_ROOT = BASE_DIR / 'staticfiles'                # Директория для сбора статических файлов

# Настройки для медиа-файлов
MEDIA_URL = '/media/'  # URL для медиа-файлов
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')          # Директория для хранения медиа-файлов

# Настройки пользовательской модели пользователя
AUTH_USER_MODEL = 'users.CustomUser'

# Настройка аутентификации для Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Настройки для работы с JWT-токенами (опционально)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Настройки документации API
SPECTACULAR_SETTINGS = {
    'TITLE': 'User Authentication API',
    'DESCRIPTION': 'API для управления пользователями и аутентификации',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Настройки allauth
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = 'none'  
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True

# Социальные провайдеры
SOCIALACCOUNT_STORE_TOKENS = True  # Сохранять токены в БД
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),  # Без значения по умолчанию
            'secret': config('GOOGLE_SECRET'),
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'yandex': {
        'APP': {
            'client_id': config('YANDEX_CLIENT_ID'),
            'secret': config('YANDEX_SECRET'),
        },
        'SCOPE': ['login:email', 'login:info'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# Настройки email 
EMAIL_BACKEND = config('EMAIL_BACKEND')               # Используемый бекенд
EMAIL_HOST = config('EMAIL_HOST')                     # SMTP-сервер
EMAIL_PORT = config('EMAIL_PORT', cast=int)           # Порт для SMTP
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)    # Использование SSL
EMAIL_HOST_USER = config('EMAIL_HOST_USER')           # Логин SMTP
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')   # Пароль SMTP
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER                  # Email отправителя
SERVER_EMAIL = EMAIL_HOST_USER                        # Email для системных уведомлений
EMAIL_ADMIN = EMAIL_HOST_USER                         # Email администратора
