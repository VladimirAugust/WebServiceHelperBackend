from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta


class Ability(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, tg_id, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not tg_id:
            raise ValueError('The given phone_number must be set')
        user = self.model(tg_id=tg_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, tg_id, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(tg_id, password, **extra_fields)

    def create_superuser(self, tg_id, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(tg_id, password, **extra_fields)


class User(AbstractUser):
    username = None

    gifts = models.IntegerField(verbose_name="Дары", default=0, validators=[MinValueValidator(settings.MIN_GIFTS_VALUE)])
    avatar = models.ImageField(verbose_name="Аватарка", upload_to="images/uploads/users/photo/", default="images/uploads/users/avatars/default.png")
    description = models.TextField(max_length=1200, default="Пользователь не написал о себе.")
    abilities = models.ManyToManyField(Ability, max_length=10, blank=True)
    city = models.CharField(verbose_name="Город проживания", max_length=100, blank=True)
    district = models.CharField(verbose_name="Район проживания", max_length=100, blank=True)
    tg_id = models.CharField(verbose_name="id телеграм", unique=True, max_length=20)
    phone_number = models.CharField(verbose_name="Номер телефона", unique=True, max_length=20, null=True, blank=True)

    block_reason = models.TextField(verbose_name="Причина блокировки", max_length=1000,
                                    default="Пользователь не заблокирован")

    USERNAME_FIELD = 'tg_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def last_seen(self):
        return cache.get('seen_%s' % self.tg_id)

    def is_online(self) -> bool:
        if self.last_seen():
            now = datetime.now()
            return now < self.last_seen() + timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
        return False
