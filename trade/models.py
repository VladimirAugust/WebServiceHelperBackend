from decimal import Decimal

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.template import loader

from common.services.telegram import multiple_send_msg


class GoodCategory(models.Model):
    name = models.CharField("Название", max_length=128)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    sort_order = models.PositiveIntegerField("✋", default=0, blank=False, null=False)
    is_service = models.BooleanField("Услуга", default=False)

    class Meta:
        verbose_name = 'Категория товаров/услуг'
        verbose_name_plural = 'Категории товаров/услуг'
        ordering = ['sort_order']

    @property
    def parents(self):
        parents = []
        current = self
        while current.parent:
            parents.append(current.parent)
            current = current.parent
        return parents


    def __str__(self):
        objects = list(reversed(self.parents))
        objects.append(self)
        return ' > '.join(map(lambda x: x.name, objects))


class Good(models.Model):
    NOT_READY_FOR_SELL = -1 # a special const to specify that a user doesn't want to sell a good for gifts/currency
    # NOT_READY_FOR_CURRENCY = Decimal(-1) # a special const to specify that a user doesn't want to sell a good for the real currency

    name = models.CharField("Название", max_length=128)
    user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, verbose_name="Автор")

    TYPE_GOOD = "good"
    TYPE_SERVICE = "service"
    TYPE_CHOICES = [
        (TYPE_GOOD, 'Товар'),
        (TYPE_SERVICE, 'Услуга'),
    ]
    type = models.CharField("Тип", max_length=20, choices=TYPE_CHOICES)

    category = models.ForeignKey(GoodCategory, on_delete=models.SET_NULL, null=True, verbose_name="Категория")

    class PublishState(models.IntegerChoices):
        DRAFT = 0, "Черновик"
        MODERATION = 1, "На модерации",
        MODERATION_DISALLOW = 2, "Запрещено модератором",
        PUBLISHED = 3, "Опубликовано",
        DELETED = 4, "Удалено",
        SOLD = 5, "Продано",
    state = models.PositiveSmallIntegerField("Состояние", choices=PublishState.choices, default=PublishState.DRAFT)

    moderation_disallow_reason = models.TextField("Причина отказа модератором", blank=True)
    description = models.TextField("Описание", blank=True)
    condition = models.PositiveSmallIntegerField("Состояние товара", default=5, null=True, validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    price_currency = models.DecimalField("Стоимость в реальной валюте", max_digits=10, decimal_places=2,
                                         default=Decimal(NOT_READY_FOR_SELL),
                                         validators=[MinValueValidator(Decimal(NOT_READY_FOR_SELL))])
    price_gifts = models.IntegerField("Стоимость в дарах", default=NOT_READY_FOR_SELL, validators=[MinValueValidator(NOT_READY_FOR_SELL)])
    ready_to_change = models.BooleanField("Готов обменять", default=False)
    contacts = models.TextField("Контакты")
    images = models.JSONField("Фотографии", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар/услуга'
        verbose_name_plural = 'Товары/услуги'

    def __str__(self):
        return f"{self.name} (id{self.id} {dict(self.PublishState.choices)[self.state]})"


@receiver(signals.post_save, sender=Good, dispatch_uid='good_updating')
def good_updated(sender, instance, created, **kwargs):
    from django.urls import reverse

    if instance.state == Good.PublishState.MODERATION:
        users = get_user_model().objects.filter(groups__id=settings.GROUP_GOODS_MODERATOR_ID)
        template = loader.get_template('telegram/good_moderation_notify.html')
        name = f"Id{instance.id} ({instance.type}) {instance.name}"
        url = settings.SITE_DOMAIN + reverse('admin:trade_good_change', args=(instance.id,))

        multiple_send_msg(users, template.render({"url": url, "name": name}), parse_mode="HTML")