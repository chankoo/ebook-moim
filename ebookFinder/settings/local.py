from ebookFinder.settings.base import *

DEBUG = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file':
                os.path.join(DJANGO_ROOT, 'settings/local_database.conf'),
        },
        'TEST': {
            'NAME': 'ebookFinder_test'
        }
    }
}

STATICFILES_DIRS = [
    os.path.join(DJANGO_ROOT, 'static'),
]

ALLOWED_HOSTS = ['*', ]

from ebookFinder import celeryconfig as CELERY_CONFIG
from .secret_key import SECRET_KEY

