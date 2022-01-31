from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.conf import settings

from datetime import datetime, timedelta

import uuid


class Ability(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class User(AbstractUser):
    gifts = models.IntegerField(verbose_name="Дары", default=0,
                                validators=[MinValueValidator(settings.MIN_GIFTS_VALUE)])
    avatar = models.ImageField(verbose_name="Аватарка", upload_to="images/uploads/users/photo/",
                               default="images/uploads/users/avatars"
                                       "/default.png")
    description = models.TextField(max_length=1200, default="Пользователь не написал о себе.")
    abilities = models.ManyToManyField(Ability, max_length=10)


class RegistrationLinkGenerator(models.Model):
    url_hash = models.CharField(default=uuid.uuid4().hex, max_length=64, editable=False)
    alive_time = models.IntegerField(verbose_name="Время жизни ссылки(дни)", default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return settings.FRONTEND_HOST + "register/" + self.url_hash

    def is_alive(self) -> bool:
        """Вернёт true, если ссылка жива, иначе false"""
        if not (self.created_at + timedelta(days=self.alive_time)).timestamp() <= datetime.now().timestamp():
            return True

        return False
