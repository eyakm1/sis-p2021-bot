from django.db import models


class Contest(models.Model):
    cid = models.BigIntegerField(unique=True, primary_key=True)
    chat_id = models.BigIntegerField()
    last_run_id = models.BigIntegerField(default=-1)
