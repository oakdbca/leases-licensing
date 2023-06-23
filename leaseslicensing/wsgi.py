"""
WSGI configuration for leases licensing project.

Exposes the WSGI callable as a module-level variable named 'application'
"""
import os
from django.core.wsgi import get_wsgi_application

import confy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
confy.read_environment_file(BASE_DIR + "/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leaseslicensing.settings")
application = get_wsgi_application()
