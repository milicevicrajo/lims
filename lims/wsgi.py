"""
WSGI config for lims project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import environ

from django.core.wsgi import get_wsgi_application
env = environ.Env()
# Dodaj apsolutnu putanju do .env fajla
environ.Env.read_env('/var/www/lims/.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', env('DJANGO_SETTINGS_MODULE'))

application = get_wsgi_application()
