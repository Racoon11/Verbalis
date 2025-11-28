from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class Language(models.Model):
    language = models.CharField("Язык", max_length=30)
    slug = models.SlugField("Слаг")
    icon = models.ImageField('Иконка', upload_to='language_images',
                             blank=True, null=True)

    class Meta:
        verbose_name = 'язык'
        verbose_name_plural = 'Языки'

    def __str__(self):
        return self.language


class UserLanguageStreak(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, default=0)
    days = models.IntegerField("Дней в ударе", default=0)
    last_updated = models.DateField(auto_now=True)

    def can_increment(self):
        return self.last_updated < timezone.now().date()

    class Meta:
        unique_together = ('user', 'language')
