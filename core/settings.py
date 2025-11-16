import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# SECURITY
# -------------------------------------------------

SECRET_KEY = "unsafe-default-key"       # ضعي مفتاحك لاحقاً لو احتجتِي

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
    "smartlock-wallet.onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "https://smartlock-wallet.onrender.com"
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ADMIN_URL = "admin/"

# -------------------------------------------------
# LANGUAGE & TIMEZONE
# -------------------------------------------------

LANGUAGE_CODE = "ar"
TIME_ZONE = "Asia/Riyadh"

USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("ar", "Arabic"),
    ("en", "English"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# -------------------------------------------------
# APPS
# -------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "drf_spectacular",
    "corsheaders",

    "bookings",
    "locks",
    "walletpass",
    "dashboard",
]

# -------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "core.urls"

# -------------------------------------------------
# TEMPLATES
# -------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "core.wsgi.application"

# -------------------------------------------------
# DATABASE (SQLite)
# -------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------
# STATIC FILES
# -------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# -------------------------------------------------
# DRF + JWT
# -------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SmartLock Cloud API",
    "DESCRIPTION": "Bookings API + TTLock + Google Wallet",
    "VERSION": "1.0.0",
}

ACCESS_TOKEN_LIFETIME_MIN = 60

# -------------------------------------------------
# GOOGLE WALLET
# -------------------------------------------------

GOOGLE_ISSUER_ID = "106815132786242054438"
GOOGLE_CLASS_SUFFIX = "roomaccess"
GOOGLE_SERVICE_ACCOUNT_EMAIL = "wallet-service@dream-c3154.iam.gserviceaccount.com"
GOOGLE_SERVICE_ACCOUNT_KEY_JSON_PATH = str(BASE_DIR / "google_wallet_key.json")

# -------------------------------------------------
# TTLOCK (Smart Lock)
# -------------------------------------------------

TTLOCK_BASE_URL = "https://api.ttlock.com.cn/v3"

TTLOCK_CLIENT_ID = "068ed449f3074fa5a8effd5c9fc49ed1"
TTLOCK_CLIENT_SECRET = "cf6f87bbef0308efa9e2b788334ad57b"

TTLOCK_USERNAME = "kh080dddd@gmail.com"
TTLOCK_PASSWORD = "shoog1999"

