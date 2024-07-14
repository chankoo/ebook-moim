from .base import *

DEBUG = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "./logs/django/error.log",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
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
        "OPTIONS": {"isolation_level": "READ COMMITTED"},
    }
}

ALLOWED_HOSTS = [
    "*",
]

# from tasks import celeryconfig as CELERY_CONFIG
