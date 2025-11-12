import os, datetime
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
# يسمح بكل شيء افتراضياً، ويمكن ضبطه عبر ALLOWED_HOSTS=domain1,domain2
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]

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
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]


ROOT_URLCONF = "core.urls"

TEMPLATES = [{
    "BACKEND":"django.template.backends.django.DjangoTemplates",
    "DIRS":[BASE_DIR/"templates"],
    "APP_DIRS":True,
    "OPTIONS":{"context_processors":[
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]}
}]
WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# إذا كان DATABASE_URL مضبوطاً (مثل Render Postgres) نستخدمه بدلاً من SQLite
if os.getenv("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.parse(
        os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=os.getenv("DB_SSL_REQUIRE", "true").lower() == "true",
    )

STATIC_URL = "static/"

# إعدادات HTTPS قابلة للضبط من البيئة
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False").lower() == "true"
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# ✅ تبقى هذه للحماية العامة
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# CORS: إن تم ضبط CORS_ALLOWED_ORIGINS فسنستخدمها، وإلا نسمح للجميع (للتجربة)
_cors_list = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
CORS_ALLOW_ALL_ORIGINS = False if _cors_list else True
CORS_ALLOWED_ORIGINS = _cors_list

# CSRF trusted origins: ضف الدومين مع البروتوكول
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES":["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_SCHEMA_CLASS":"drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES":[
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES":{"user":"120/min","anon":"30/min"},
}

SPECTACULAR_SETTINGS = {
    "TITLE":"SmartLock Cloud API",
    "DESCRIPTION":"Booking ↔ Smart Lock ↔ Google Wallet",
    "VERSION":"1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ✅ Celery
REDIS_URL = os.getenv("REDIS_URL")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TIMEZONE = "UTC"
