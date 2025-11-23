from django.db import models


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
