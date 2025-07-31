from django.apps import AppConfig
import mpesa
from django.conf import settings
import logging  

try:
    import mpesa
    MPESA_APP_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("'mpesa' Django app found. Assuming configuration will be handled via settings.py.")
except ImportError:
    mpesa = None
    MPESA_APP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("'mpesa' Django app could not be imported. M-Pesa features will be disabled. Ensure 'django-mpesa' is installed and 'mpesa' is in INSTALLED_APPS.")


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self):
        if MPESA_APP_AVAILABLE:
            logger.info("Main app and 'django-mpesa' app are ready.")
        else:
            logger.info("Main app ready. 'django-mpesa' is not available.")