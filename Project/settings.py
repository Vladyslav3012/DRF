import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = True

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

    'flights.apps.FlightsConfig',
    'users.apps.UsersConfig',
    'airports.apps.AirportsConfig',
    'airplanes.apps.AirplanesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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

WSGI_APPLICATION = 'Project.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ["DATABASE_NAME"],
        'USER': os.environ["DATABASE_USER"],
        'PASSWORD': os.environ["DATABASE_PASSWORD"],
        'HOST': os.environ.get("DATABASE_HOST", "db"),
        'PORT': os.environ.get("DATABASE_PORT", '5432'),
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
        'drf_spectacular.openapi.AutoSchema'
    ,
    'DEFAULT_PERMISSION_CLASSES': [
          'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS':
        ['django_filters.rest_framework.DjangoFilterBackend'],
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'Airport API',
    'DESCRIPTION': 'In this API you can buy ticket to fly',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=int(os.environ["ACCESS_TOKEN_LIFETIME"])),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ["REFRESH_TOKEN_LIFETIME"])),
    "AUTH_HEADER_TYPES": (os.environ["AUTH_HEADER_TYPES"],),
}

STRIPE_PUBLIC_KEY = os.environ["STRIPE_PUBLIC_KEY"]
STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

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

SECRET_TOKEN_TO_WEBHOOK = os.environ['SECRET_TOKEN_TO_WEBHOOK']

if DEBUG:
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE += ['silk.middleware.SilkyMiddleware']

