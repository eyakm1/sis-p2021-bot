from django.db import models


class Contest(models.Model):
    cid = models.BigIntegerField(unique=True, primary_key=True)
    last_run_id = models.BigIntegerField(default=-1)
