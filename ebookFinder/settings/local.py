from ebookFinder.settings.base import *

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

from ebookFinder import celeryconfig as CELERY_CONFIG