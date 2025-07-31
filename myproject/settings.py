from pathlib import Path
import mpesa
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-d8b=hoi%x8t^n@$2e554uy4-he9lz76u0gz8b#p35mqzx&#eu@"
DEBUG = True

ALLOWED_HOSTS = []

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
    "whitenoise.middleware.WhiteNoiseMiddlewar",
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

'default': dj_database_url.config(
        default=f"postgres://{os.environ.get('DB_USER', 'mealy_user')}:{os.environ.get('DB_PASSWORD', 'your_secure_password')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'mealy_db')}",
        conn_max_age=600,
        conn_health_checks=True,
    )

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
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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
