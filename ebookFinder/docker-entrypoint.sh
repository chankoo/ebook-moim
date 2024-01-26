#!/bin/bash

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

python manage.py makemigrations && python manage.py migrate

mkdir -p ./logs/django && touch ./logs/django/error.log
mkdir -p ./logs/uvicorn && touch ./logs/uvicorn/error.log

uvicorn asgi:application --workers 1 --host 0.0.0.0 --port 8000 --reload --limit-concurrency 128 --log-level error --log-config ./logs/uvicorn/log.ini
