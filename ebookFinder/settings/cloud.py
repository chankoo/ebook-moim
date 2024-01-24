from .base import *

DEBUG = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': './logs/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

import pymysql

pymysql.install_as_MySQLdb()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ebook_moim",
        "USER": "root",
        "PASSWORD": "root",
        "HOST": "mysql-ebook-moim",
        "PORT": "3306",
        "OPTIONS": {
            "isolation_level": "READ COMMITTED"
        }
    }
}

ALLOWED_HOSTS = ['*', ]

SERVICE_DOMAIN = 'http://43.200.179.231/'

# from tasks import celeryconfig as CELERY_CONFIG