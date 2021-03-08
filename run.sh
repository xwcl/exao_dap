#!/usr/bin/env bash
env/bin/python manage.py collectstatic --no-input
env/bin/python manage.py migrate
env/bin/gunicorn exao_dap.wsgi --bind 0.0.0.0:8000
