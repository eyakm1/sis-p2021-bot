# !/usr/bin/env python

# import this file if you want to use ORM in your feature
# DO NOT FORGET TO INCLUDE YOUR APP IN SETTINGS FILE
# Django specific settings
import os

# Run ORM setup.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'common.django_conf.settings')
try:
    import django
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc
django.setup()
