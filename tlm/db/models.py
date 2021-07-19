from django.db import models


# Sample User model
class User(models.Model):
    name = models.CharField(max_length=50, default="")

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return self.name
