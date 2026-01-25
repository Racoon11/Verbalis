from django.db import models
from django.contrib.auth import get_user_model
from words.models import Word


User = get_user_model()


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField(auto_now_add=True)


class ChosenWords(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)


class RecommendedWords(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    model = models.CharField(max_length=300)


class AcceptedRecs(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
