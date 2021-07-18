# Django specific settings
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import your models for use in your script

from db.models import *

# Seed a few users in the database
User.objects.create(name='Dan')
User.objects.create(name='Robert')

for u in User.objects.all():
    print(f'ID: {u.id} \tUsername: {u.name}')