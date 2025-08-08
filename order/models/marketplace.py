from django.db import models

from order.constants import MARKETPLACE, MARKETPLACES


class Marketplace(models.Model):
    title = models.CharField("Наименование", max_length=50, unique=True)
    url = models.CharField("URL маркетплейса", max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = MARKETPLACE
        verbose_name_plural = MARKETPLACES
        ordering = ("title", )
