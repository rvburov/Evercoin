import os
from pathlib import Path
from decouple import config  # Импорт библиотеки для управления переменными окружения

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

# Локальные приложения проекта (созданные пользователем)
LOCAL_APPS = [
    'api',
    'users',
]

# Сторонние приложения, установленные через pip
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
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
    'corsheaders.middleware.CorsMiddleware',
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

# Внутренние IP-адреса для отладки
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1']

# Настройки пользовательской модели пользователя
AUTH_USER_MODEL = 'users.CustomUser'

# ===== Настройки DRF =====
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ===== Настройки документации API =====
SPECTACULAR_SETTINGS = {
    'TITLE': 'Authentication API',
    'DESCRIPTION': 'API для аутентификации пользователей',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}

# ===== JWT Настройки =====
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ===== CORS Настройки =====
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')

# ===== OAuth Настройки =====
OAUTH_PROVIDERS = {
    'google': {
        'client_id': config('GOOGLE_OAUTH_CLIENT_ID', default=''),
        'client_secret': config('GOOGLE_OAUTH_CLIENT_SECRET', default=''),
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'userinfo_url': 'https://www.googleapis.com/oauth2/v3/userinfo',
        'scopes': ['openid', 'email', 'profile'],
        'redirect_uri': config('GOOGLE_REDIRECT_URI', default='http://localhost:8000/oauth/google/callback/')
    },
    'yandex': {
        'client_id': config('YANDEX_OAUTH_CLIENT_ID', default=''),
        'client_secret': config('YANDEX_OAUTH_CLIENT_SECRET', default=''),
        'authorize_url': 'https://oauth.yandex.ru/authorize',
        'token_url': 'https://oauth.yandex.ru/token',
        'userinfo_url': 'https://login.yandex.ru/info',
        'scopes': ['login:email', 'login:info'],
        'redirect_uri': config('YANDEX_REDIRECT_URI', default='http://localhost:8000/oauth/yandex/callback/')
    }
}

# URL для перенаправления после успешной OAuth-аутентификации
OAUTH_SUCCESS_REDIRECT_URL = config('OAUTH_SUCCESS_REDIRECT_URL', default='http://localhost:3000/login/success')
OAUTH_FAILURE_REDIRECT_URL = config('OAUTH_FAILURE_REDIRECT_URL', default='http://localhost:3000/login/error')

# ===== Настройки аутентификации =====
AUTH_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'authentication.oauth.backends.OAuthBackend',
]

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
