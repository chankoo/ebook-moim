#!/bin/bash

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

python manage.py makemigrations && python manage.py migrate

uvicorn asgi:application --workers 1 --host 0.0.0.0 --port 8000 --reload
