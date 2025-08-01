from pathlib import Path
import mpesa
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-d8b=hoi%x8t^n@$2e554uy4-he9lz76u0gz8b#p35mqzx&#eu@"


ALLOWED_HOSTS = [
    'mealy-backend-2n74.onrender.com',
    'localhost',  # For local development
    '127.0.0.1',  # For local development
                ]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders", 
    'myapp',
    "mpesa",
    "django_daraja",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware", 
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(  # No extra colons or annotations
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    "https://mealy-frontend-git-main-wayne-kimanis-projects.vercel.app",
    "https://mealy-frontend-m21um18cs-wayne-kimanis-projects.vercel.app",
    "https://mealy-frontend-six.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = False

load_dotenv()

MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
MPESA_EXPRESS_SHORTCODE = os.getenv('MPESA_SHORT_CODE')
MPESA_PASSKEY = os.getenv('MPESA_PASS_KEY')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL')

MPESA_CONFIG = {
    'CONSUMER_KEY': os.getenv('MPESA_CONSUMER_KEY'),
    'CONSUMER_SECRET': os.getenv('MPESA_CONSUMER_SECRET'),
    'CERTIFICATE_FILE': None,
    'HOST_NAME': os.getenv('MPESA_HOST_NAME', 'https://yourdomain.com'),
    'PASS_KEY': os.getenv('MPESA_PASS_KEY'),
    'SAFARICOM_API': os.getenv('MPESA_API_URL', 'https://sandbox.safaricom.co.ke'),
    'AUTH_URL': '/oauth/v1/generate?grant_type=client_credentials',
    'STK_PUSH_URL': '/mpesa/stkpush/v1/processrequest',
    'TRANSACTION_STATUS_URL': '/mpesa/transactionstatus/v1/query',
    'CALLBACK_URL': 'https://yourdomain.com/mpesa-callback/',
    'ACCOUNT_REFERENCE': 'YOUR_APP_NAME',
    'TRANSACTION_TYPE': 'CustomerPayBillOnline',
    'BUSINESS_SHORT_CODE': os.getenv('MPESA_SHORT_CODE'),
}
