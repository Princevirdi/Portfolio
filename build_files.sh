#!/bin/bash

echo "BUILD START"

pip install -r requirements.txt
python manage.py collectstatic whitenoise gunicorn --noinput

echo "BUILD END"