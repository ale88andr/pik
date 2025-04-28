from django.conf import settings
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
            or_lookup = (Q(title__icontains=query) | Q(order_price__icontains=query) | Q(buy_price__icontains=query) | Q(track_num__icontains=query))
            qs = qs.filter(or_lookup)

        return qs


class Order(models.Model):

    class Status(models.IntegerChoices):
        DRAFT = 0, "Оформлен"
        BUYED = 1, "Выкуплен"
        IN_DELIVERY = 2, "Доставляется в ТК"
        DELIVERED = 3, "Доставлен в ТК"
        ARRIVED = 4, "Прибыл в пункт"
        CANCELLED = 5, "Отменен"

    objects = OrderManager()

    title = models.CharField("Наименование товара", max_length=200)
    img = models.ImageField("Изображение товара", upload_to=IMG_MEDIA_DIR, null=True, blank=True)
    order_price = models.DecimalField("Цена заказа", max_digits=5, decimal_places=2, help_text="Цена товара при оформлении заказа в ¥")
    buy_price = models.DecimalField("Цена покупки", max_digits=5, decimal_places=2, default=0, help_text="Цена товара при выкупе")
    exchange = models.DecimalField("Курс при покупке", max_digits=5, decimal_places=2, default=0, help_text="Курс валюты при выкупе")
    weight = models.IntegerField("Вес", null=True, blank=True, default=0, help_text="Вес товара")
    quantity = models.IntegerField("Количество", default=1)
    track_num = models.CharField("Трек номер", max_length=200, null=True, blank=True, help_text="Номер отслеживания заказа")
    url = models.URLField("Ссылка", help_text="Ссылка на товар")
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT, verbose_name="Закупка", related_name="purchase_orders")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="Покупатель", related_name="customer_orders")
    marketplace = models.ForeignKey(Marketplace, on_delete=models.PROTECT, verbose_name="Маркетплейс", null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, default=Status.DRAFT, verbose_name="Статус")

    created_at = models.DateField("Созданно", default=timezone.now)

    @cached_property
    def display_img(self):
        """Функция, возвращающая HTML тег img с изображением"""
        return format_html(
            f'<img src="{self.img.url}" width="{IMG_WIDTH}">' if self.img else NO_IMAGE_HTML
        )

    @property
    def get_status(self):
        return self.get_status_display()

    def close(self, dt):
        self.closed_date = dt
        self.save()

    def open(self, dt):
        self.opened_date = dt
        self.save()

    @property
    def exchange_rate(self):
        return self.exchange if self.exchange else self.purchase.exchange

    def calculate_weight(self):
        return self.weight * self.quantity if self.weight else 0

    def calculate_buy_exchange_price(self):
        return round(self.quantity * self.buy_price * self.exchange_rate, 2) if self.exchange_rate and self.buy_price else 0

    def calculate_order_exchange_price(self):
        return round(self.quantity * self.order_price * self.exchange_rate, 2) if self.exchange_rate and self.order_price else 0

    def calculate_difference(self):
        return round(self.quantity * self.difference * self.exchange_rate, 2) if self.difference and self.order_price else 0

    def calculate_difference_tax(self):
        return round(self.quantity * self.difference_tax * self.exchange_rate, 2) if self.difference_tax and self.order_price else 0

    @property
    def difference(self):
        if not self.order_price or self.buy_price <= 0:
            return None
        return (self.order_price - self.buy_price) * self.quantity

    @property
    def difference_tax(self):
        if not self.order_price or self.buy_price <= 0:
            return None
        return (self.order_price * self.customer.tax / 100) * self.quantity

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ORDER
        verbose_name_plural = ORDERS
        ordering = ("created_at", )
