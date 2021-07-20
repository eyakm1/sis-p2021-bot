# You should include this file if you want to use ORM in your feature
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
