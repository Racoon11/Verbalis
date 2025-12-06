from django.db import models
from django.contrib.auth import get_user_model
from languages.models import Language


User = get_user_model()


class Word(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    word = models.CharField('Слово на иностранном языке', max_length=100)
    word_translate = models.CharField('Перевод на русский', max_length=100)
    part_of_speach = models.CharField('Часть речи', max_length=30)

    class Meta:
        verbose_name = 'слово'
        verbose_name_plural = 'Слова'

    def __str__(self):
        return self.word


class UserWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    added_date = models.DateField(auto_now_add=True)
    train_number = models.IntegerField(default=0)
    next_train_date = models.DateField(auto_now_add=True)


class Sentence(models.Model):
    sentence = models.CharField("Предложение", max_length=300)
    words = models.ManyToManyField(Word, verbose_name="слова в предложении")

    class Meta:
        verbose_name = 'предложение'
        verbose_name_plural = 'Предложения'

    def __str__(self):
        return self.sentence


class Collection(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, related_name="owner_set")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=400)
    creation_date = models.DateField(auto_now_add=True)
    is_public = models.BooleanField()
    words = models.ManyToManyField(Word)
    users = models.ManyToManyField(User,
                                   through="CollectionRating",
                                   related_name="rate_users_set")

    class Meta:
        verbose_name = 'коллекция'
        verbose_name_plural = 'Коллекции'

    def __str__(self):
        return self.name


class CollectionRating(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
