# -*- coding:utf-8 -*-
from __future__ import absolute_import

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ebookFinder.settings.local')

app = Celery('ebookFinder')

app.config_from_object(settings.CELERY_CONFIG)
app.autodiscover_tasks()
