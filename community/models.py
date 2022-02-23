from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Community(models.Model):
    title = models.CharField(verbose_name="Название Сообщества", max_length=32)
    description = models.TextField(verbose_name="Описание Сообщества", max_length=3000)
    owner = models.ForeignKey(
            User,
            related_name="Owner",
            verbose_name="Глава сообщества", 
            on_delete=models.CASCADE)
    members = models.ManyToManyField(
            User,
            related_name="Members",
            verbose_name="Участники группы"
    )

    def __str__(self):
        return self.title

