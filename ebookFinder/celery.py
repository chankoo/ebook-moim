# -*- coding:utf-8 -*-
from __future__ import absolute_import

import os
import json
from django.conf import settings
from celery import Celery

config = {}
if os.path.isfile("./config.json"):
    with open("./config.json") as fp:
        config = json.load(fp)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f"ebookFinder.settings.{config.get('env', 'local')}")

app = Celery('ebookFinder')

app.config_from_object(settings.CELERY_CONFIG)
app.autodiscover_tasks()
