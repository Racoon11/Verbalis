from django.contrib.auth.models import AbstractUser
from django.db import models
from languages.models import Language


class VerbalisUser(AbstractUser):
    cur_language = models.ForeignKey(Language,
                                     on_delete=models.SET_NULL,
                                     verbose_name='Изучаемый язык',
                                     null=True,
                                     blank=True)
    image = models.ImageField('Фото', upload_to='users_images',
                              blank=True, null=True)


class Following(models.Model):
    following_user = models.ForeignKey(VerbalisUser,
                                       on_delete=models.CASCADE,
                                       related_name='following_set')
    followed_user = models.ForeignKey(VerbalisUser,
                                      on_delete=models.CASCADE,
                                      related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('following_user', 'followed_user')
