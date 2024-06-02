#!/bin/sh
# source /usr/src/app/venv/bin/activate

which python3
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000