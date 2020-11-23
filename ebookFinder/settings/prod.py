from ebookFinder.settings.base import *

DEBUG = False

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(DJANGO_ROOT, 'settings/prod_database.conf'),
        },
        'TEST': {
            'NAME': 'ebook_moim'
        }
    }
}

STATICFILES_DIRS = [
    os.path.join(DJANGO_ROOT, 'static'),
]

ALLOWED_HOSTS = ['*', ]

from ebookFinder import celeryconfig as CELERY_CONFIG
from .secret_key import SECRET_KEY

