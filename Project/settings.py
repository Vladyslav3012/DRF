import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY", 'xxx')

DEBUG = False

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'users.CustomUser'

NGROK_DOMAIN = 'https://else-semisolemn-meta.ngrok-free.dev'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'drf_spectacular',
    'django_filters',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    
    'flights.apps.FlightsConfig',
    'users.apps.UsersConfig',
    'airports.apps.AirportsConfig',
    'airplanes.apps.AirplanesConfig',
    'assistant.apps.AssistantConfig',
    'orders.apps.OrdersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI_APPLICATION = 'Project.wsgi.application'
ASGI_APPLICATION = "Project.asgi.application"


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("DATABASE_NAME", 'Airport'),
        'USER': os.environ.get("DATABASE_USER", 'postgres'),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD", 'password'),
        'HOST': os.environ.get("DATABASE_HOST", "db"),
        'PORT': os.environ.get("DATABASE_PORT", '5432'),
    }
}

db_from_render = dj_database_url.config(conn_max_age=600)

DATABASES['default'].update(db_from_render)

CACHES = {
    "default": {
        "BACKEND":
            "django.core.cache.backends.redis.RedisCache",
        "LOCATION":
        "redis://127.0.0.1:6379"
    }
}

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

LANGUAGE_CODE = 'UK'

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS':
        'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
          'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
            'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'Airport API',
    'DESCRIPTION': 'In this API you can buy ticket to fly',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("ACCESS_TOKEN_LIFETIME", 5))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("REFRESH_TOKEN_LIFETIME", 30))),
    "AUTH_HEADER_TYPES": (os.environ.get("AUTH_HEADER_TYPES", 'Bearer'),),
}

STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", 'key')
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", 'key')
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", 'key')

CSRF_TRUSTED_ORIGINS = [
    "https://else-semisolemn-meta.ngrok-free.dev",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
        "verbose": {
            "format": "[{asctime}] {levelname} {name} :: {message}",
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": (BASE_DIR / "django.log"),
            "formatter": "verbose",
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django.utils.autoreload": {
            "handlers": [],
            "level": "CRITICAL",
            "propagate": False,
        },
    },

}

SECRET_TOKEN_TO_WEBHOOK = os.environ.get('SECRET_TOKEN_TO_WEBHOOK', 'key')

if DEBUG:
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE += ['silk.middleware.SilkyMiddleware']


GEMINI_SECRET_KEY = (os.environ.get('GEMINI_SECRET_KEY', 'key'))
CORS_ALLOW_ALL_ORIGINS = True


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', "key")
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD' 'key')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', "key")

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'key')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', "key")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
