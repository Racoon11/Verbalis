from django.db import models
from languages.models import Language
from django.contrib.auth import get_user_model


User = get_user_model()


class TrainingModule(models.Model):
    name = models.CharField("Название модуля", max_length=30)
    description = models.CharField("Описание модуля", max_length=100)
    displayed = models.CharField("Короткое название",
                                 max_length=30, default='')
    base_order = models.IntegerField("Базовый порядок модуля",
                                     default=None, null=True)

    class Meta:
        verbose_name = 'модуль тренировки слов'
        verbose_name_plural = 'Модули'

    def __str__(self):
        return self.name


class UserLanguageTraining(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    training = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'order', 'language')
