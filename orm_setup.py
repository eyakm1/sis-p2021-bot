# import this file if you want to use ORM in your feature
# DO NOT FORGET TO INCLUDE YOUR APP IN SETTINGS FILE
# Django specific settings
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
