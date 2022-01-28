from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from taggit.managers import TaggableManager


class Card(models.Model):
    cid = models.PositiveIntegerField(db_index=True, unique=True)
    group = models.CharField(max_length=20)
    question = models.CharField(max_length=200, default="none", blank=False)
    answer = models.CharField(max_length=200, default="none", blank=False)
    example = models.CharField(max_length=200)
    translation = models.CharField(max_length=200)
    extra = models.CharField(max_length=200)
    tags = TaggableManager()

    def __str__(self):
        return self.question

    class Meta:
        ordering = ('cid',)
        # verbose_name = 'category'
        # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('flashcards:card_detail',
                       args=[self.id])


# 每次使用时的数据，作为外键与卡片绑定

class Recitedata(models.Model):
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    rank = models.PositiveIntegerField(verbose_name="easy or diff?", default=0)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="recitedata")

    def __str__(self):
        return str(self.date) + ":" + str(self.rank)

    class Meta:
        ordering = ('date',)


class WordList(models.Model):
    owner = models.ForeignKey(User, models.CASCADE, related_name='owner')
    name = models.CharField(max_length=20, blank=False)
    wordlist = models.CharField(max_length=20000, blank=False)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    progress = models.PositiveIntegerField(blank=False, default=0)
    len_list = models.PositiveIntegerField(blank=False, default=50)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('date',)
