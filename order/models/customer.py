from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

from order.constants import CUSTOMER, CUSTOMERS


validate_phone = RegexValidator(r'^(\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}$', "Номер телефона некорректен! Формат ввода +7(777) 777-77-77")
validate_telegram = RegexValidator(r'^[a-zA-Z0-9_]*$', "Telegram ID некоректен!")


class CustomerManager(models.Manager):
    use_for_related_fields = True

    def search(self, query=None):
        qs = self.get_queryset()

        if query:
            or_lookup = (Q(name__icontains=query) | Q(phone__icontains=query) | Q(telegram_id__icontains=query))
            qs = qs.filter(or_lookup)

        return qs


class Customer(models.Model):

    objects = CustomerManager()

    name = models.CharField(
        "Имя",
        max_length=200
    )
    phone = models.CharField(
        "Номер телефона",
        max_length=50,
        blank=True,
        null=True,
        validators=[validate_phone],
        help_text="Номер в формате +7(xxx)xxx-xx-xx"
    )
    telegram_id = models.CharField(
        "Telegram ID",
        max_length=50,
        blank=True,
        null=True,
        validators=[validate_telegram],
        help_text="Идентификатор telegram (символы после @)"
    )
    tax = models.IntegerField(
        "Комиссия %",
        default=0,
        validators=[MaxValueValidator(100), MinValueValidator(0)],
        help_text="Комиссия (в процентах), взымаемая с клиента"
    )

    created_at = models.DateTimeField("Создан", default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = CUSTOMER
        verbose_name_plural = CUSTOMERS
        ordering = ('name', )
