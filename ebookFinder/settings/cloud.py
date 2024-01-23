from ebookFinder.settings.base import *

DEBUG = False

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