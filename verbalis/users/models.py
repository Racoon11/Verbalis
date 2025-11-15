from django.contrib.auth.models import AbstractUser
from django.db import models


class VerbalisUser(AbstractUser):
    cur_language = models.IntegerField("изучаемый язык", blank=True, null=True)
