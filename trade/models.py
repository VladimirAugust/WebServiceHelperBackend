from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class GoodCategory(models.Model):
    name = models.CharField("Название", max_length=128)
    sort_order = models.PositiveIntegerField("✋", default=0, blank=False, null=False)

    class Meta:
        verbose_name = 'Категория товаров/услуг'
        verbose_name_plural = 'Категории товаров/услуг'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class Good(models.Model):
    NOT_READY_FOR_SELL = -1 # a special const to specify that a user doesn't want to sell a good for gifts/currency
    # NOT_READY_FOR_CURRENCY = Decimal(-1) # a special const to specify that a user doesn't want to sell a good for the real currency

    name = models.CharField("Название", max_length=128)

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
        PUBLISHED = 3, "Опубликовано"
    state = models.PositiveSmallIntegerField("Состояние", choices=PublishState.choices, default=PublishState.DRAFT)

    description = models.TextField("Описание")
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

    class Meta:
        verbose_name = 'Товар/услуга'
        verbose_name_plural = 'Товары/услуги'

    def __str__(self):
        return f"\"{self.name}\"  (id{self.id} state={self.state})"
