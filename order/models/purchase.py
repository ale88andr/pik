from django.conf import settings
from django.db import models
from django.utils import timezone

from order.constants import PURCHASE, PURCHASES


class Purchase(models.Model):
    title = models.CharField("Идентификатор", max_length=200, unique=True, help_text="Наименование закупки")
    opened_date = models.DateField("Дата открытия", blank=True, null=True, help_text="Дата начала закупки")
    closed_date = models.DateField("Дата закрытия", blank=True, null=True, help_text="Дата ококнчания закупки")
    weight = models.DecimalField("Вес посылки", null=True, blank=True, decimal_places=2, max_digits=7, help_text="Вес посылки")
    dilivery_cost1 = models.DecimalField("Стоимость доставки МСК", null=True, blank=True, decimal_places=2, max_digits=10, help_text="Стоимость доставки ТК до Москвы")
    dilivery_cost2 = models.DecimalField("Стоимость доставки Севастополь", null=True, blank=True, decimal_places=2, max_digits=10, help_text="Стоимость доставки до пункта назначения")
    other_expenses = models.DecimalField("Инные расходы", default=0, decimal_places=2, max_digits=10, help_text="Инные расходы на закупку")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Инициатор", null=True, blank=True)
    exchange = models.DecimalField("Курс закупки", max_digits=5, decimal_places=2, help_text="Курс валюты закупки")
    created_at = models.DateTimeField("Создано", default=timezone.now)

    def close(self, dt):
        self.closed_date = dt
        self.save()

    def open(self, dt):
        self.opened_date = dt
        self.save()

    @property
    def is_opened(self):
        return self.closed_date is None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = PURCHASE
        verbose_name_plural = PURCHASES
        ordering = ("opened_date", )
