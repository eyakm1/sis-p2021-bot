import orm_setup as _
# this is how you should import ypur models
from tlm.models import User

User.objects.create(name='Dan')
for user in User.objects.all():
    print(f"ID: {user.pk} Name:{user.name}")
