"""
MantaHotel — Django Settings
============================
Complete configuration for the MantaHotel PMS.
Uses django-environ to load settings from .env file.
"""
import os
from pathlib import Path

import environ

# ── Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Environment Variables ──────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    TIMEZONE=(str, 'Asia/Makassar'),
    HOTEL_NAME=(str, 'MantaHotel'),
    HOTEL_TAX_RATE=(int, 10),
    HOTEL_SERVICE_CHARGE=(int, 11),
)

# Read .env file if it exists
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

# ── Core Settings ──────────────────────────────────────
SECRET_KEY = env('SECRET_KEY', default='dev-insecure-key-change-in-production')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ── Application Definition ─────────────────────────────
INSTALLED_APPS = [
    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'django_htmx',

    # MantaHotel apps
    'apps.core',
    'apps.accounts',
    'apps.dashboard',
    'apps.rooms',
    'apps.guests',
    'apps.reservations',
    'apps.frontdesk',
    'apps.housekeeping',
    'apps.billing',
    'apps.inventory',
    'apps.pos',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'apps.core.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'manta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.hotel_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'manta.wsgi.application'

# ── Database ───────────────────────────────────────────
# Uses PostgreSQL (Supabase) if DB_PASSWORD is set, otherwise SQLite for local dev.
_db_password = env('DB_PASSWORD', default='')

if _db_password:
    # Production: Supabase PostgreSQL via Transaction Pooler (port 6543)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='postgres'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': _db_password,
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='6543'),
            'DISABLE_SERVER_SIDE_CURSORS': True,  # Required for Supabase transaction pooler
            'OPTIONS': {
                'connect_timeout': 10,
            },
        }
    }
else:
    # Local development: SQLite (no setup needed)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Custom User Model ─────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

# ── Password Validation ───────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Authentication ─────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG

# ── Internationalization ───────────────────────────────
LANGUAGE_CODE = 'id'
TIME_ZONE = env('TIMEZONE')
USE_I18N = True
USE_TZ = True

# ── Static Files ───────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ── Media Files ────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Default Primary Key ───────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Security (Production) ─────────────────────────────
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True

# ── Hotel Configuration ───────────────────────────────
# These are loaded into template context via context_processor
HOTEL_NAME = env('HOTEL_NAME')
HOTEL_TAX_RATE = env('HOTEL_TAX_RATE')
HOTEL_SERVICE_CHARGE = env('HOTEL_SERVICE_CHARGE')
