from decimal import Decimal
from typing import Literal
from django.db.models import Q
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import format_html

from order.constants import IMG_MEDIA_DIR, ORDER, ORDERS, IMG_WIDTH, NO_IMAGE_HTML

from .purchase import Purchase
from .customer import Customer
from .marketplace import Marketplace


class OrderManager(models.Manager):
    use_for_related_fields = True

    def search(self, query=None):
        qs = self.get_queryset()

        if query:
            normalized_query = query.strip().replace(",", ".")
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(order_price__icontains=normalized_query) |
                Q(buy_price__icontains=normalized_query) |
                Q(track_num__icontains=query)
            )

        return qs.select_related("customer", "purchase", "marketplace")


class Order(models.Model):

    class Status(models.IntegerChoices):
        DRAFT = 0, "Оформлен"
        BUYED = 1, "Выкуплен"
        IN_DELIVERY = 2, "Доставляется в ТК"
        DELIVERED = 3, "Доставлен в ТК"
        ARRIVED = 4, "Прибыл в пункт"

    objects = OrderManager()

    title = models.CharField("Наименование товара", max_length=200)
    img = models.ImageField("Изображение товара", upload_to=IMG_MEDIA_DIR, null=True, blank=True)

    order_price = models.DecimalField(
        "Цена заказа", max_digits=10, decimal_places=2,
        help_text="Цена товара при оформлении заказа в ¥"
    )
    buy_price = models.DecimalField(
        "Цена выкупа", max_digits=10, decimal_places=2, default=0,
        help_text="Цена товара при выкупе"
    )
    exchange = models.DecimalField(
        "Курс выкупа", max_digits=6, decimal_places=2, default=0,
        help_text="Курс валюты при выкупе"
    )
    weight = models.PositiveIntegerField(
        "Вес", null=True, blank=True, default=0,
        help_text="Вес товара в граммах"
    )
    track_num = models.CharField(
        "Трек номер", max_length=200, null=True, blank=True,
        help_text="Номер отслеживания заказа"
    )
    url = models.URLField("Ссылка", help_text="Ссылка на товар")
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE,
        verbose_name="Закупка", related_name="purchase_orders"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT,
        verbose_name="Покупатель", related_name="customer_orders"
    )
    marketplace = models.ForeignKey(
        Marketplace, on_delete=models.PROTECT,
        verbose_name="Маркетплейс", null=True, blank=True
    )
    status = models.IntegerField(
        choices=Status.choices, default=Status.DRAFT,
        verbose_name="Статус"
    )

    buyed_at = models.DateTimeField("Дата выкупа", null=True, blank=True)
    created_at = models.DateField("Создано", default=timezone.now)

    def __str__(self):
        return f"Заказ №{self.pk} — {self.title or 'без названия'}"

    @cached_property
    def display_img(self):
        """Функция, возвращающая HTML тег img с изображением"""
        return format_html(
            f'<img src="{self.img.url}" width="{IMG_WIDTH}">' if self.img else NO_IMAGE_HTML
        )

    @property
    def get_status(self):
        return self.get_status_display()

    @property
    def exchange_rate(self):
        return self.exchange if self.exchange else self.purchase.exchange

    def get_calculated_data(self, is_for_customer=False):
        exchange_price = (
            self.calculate_customer_order_exchange_price()
            if is_for_customer
            else self.calculate_order_exchange_price()
        )

        total_price = exchange_price + self.calculate_difference_tax()

        return [
            "",
            self.title,
            self.url,
            self.get_status,
            self.order_price,
            self.purchase.exchange,
            exchange_price,
            f"{self.customer.tax} %",
            self.calculate_difference_tax(),
            total_price,
            self.track_num,
            self.weight,
            self.customer.name
        ]

    @property
    def export_data_for_cargo(self):
        return [self.title, self.track_num,]

    def calculate_weight(self):
        return self.weight if self.weight else 0

    def calculate_buy_exchange_price(self):
        return round(self.buy_price * self.exchange_rate, 2) if self.exchange_rate and self.buy_price else 0

    def calculate_order_exchange_price(self):
        return round(self.order_price * self.exchange_rate, 2) if self.exchange_rate and self.order_price else 0

    def calculate_customer_order_exchange_price(self):
        return round(self.order_price * self.purchase.exchange, 2) if self.purchase.exchange and self.order_price else 0

    def calculate_difference(self):
        return round(self.difference * self.exchange_rate, 2) if self.difference and self.order_price else 0

    def calculate_difference_tax(self):
        return round(self.tax * self.purchase.exchange, 2) if self.tax and self.order_price else 0

    @property
    def difference(self):
        if not self.order_price or self.buy_price <= 0:
            return None
        return (self.order_price - self.buy_price)

    @property
    def tax(self) -> Decimal | Literal[0]:
        """Подсчет комиссии за товар

        Возвращаемое значение:
            int: цена товара * комиссия клиента
        """
        if not self.order_price or self.buy_price < 0:
            return 0
        return (self.order_price * self.customer.tax / 100)

    @property
    def get_difference(self):
        """Подсчет разницы цены заказа и цены выкупа товара с учетом курса

        Возвращаемое значение:
            int: разница цен или 0
        """
        if self.buy_price and self.order_price:
            diff = self.order_price * self.purchase.exchange - self.buy_price * self.exchange_rate
            return round(diff, 2)

        return 0

    @property
    def get_total_profit(self):
        """Доход с товара

        Возвращаемое значение:
            int: комиссия клиента + разница заказ-выкуп
        """
        return self.calculate_difference_tax() + self.get_difference

    def save(self, *args, **kwargs):
        if not self.pk:
            for mps in Marketplace.objects.all():
                for mp in mps.url.split(","):
                    if self.url.startswith(mp):
                        self.marketplace = mp
                        break

        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ORDER
        verbose_name_plural = ORDERS
        ordering = ("created_at", )
