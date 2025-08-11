from dataclasses import fields
from django import forms

from order.forms.base import BaseForm
from order.models.customer import Customer
from order.models.marketplace import Marketplace
from order.models.order import Order
from order.models.purchase import Purchase

class OrderForm(BaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_select_class = "form-select mb-3"
        default_checkbox_class = "form-check-input mb-3"

        if self.fields.get("customer"):
            self.fields["customer"].widget.attrs['class'] = default_select_class
        if self.fields.get("purchase"):
            self.fields["purchase"].widget.attrs['class'] = default_select_class
        if self.fields.get("marketplace"):
            self.fields["marketplace"].widget.attrs['class'] = default_select_class
        if self.fields.get("status"):
            self.fields["status"].widget.attrs['class'] = default_select_class

    class Meta:
        model = Order
        fields = "__all__"
        exclude = ("created_at", "buyed_at")


class BuyOrderForm(OrderForm):

    class Meta:
        model = Order
        fields = (
            "buy_price",
            "exchange",
        )


class SetTrackNumOrderForm(OrderForm):

    class Meta:
        model = Order
        fields = (
            "track_num",
        )


class SetArrivedOrderForm(OrderForm):

    track_orders = forms.ModelMultipleChoiceField(
        label="Другие заказы под этим трек номером",
        queryset=Order.objects.all(),
        required=False,
        help_text="Выделенные заказы будут обработанны как доставленные, с нулевым весом"
    )

    class Meta:
        model = Order
        fields = (
            "weight",
            "track_orders"
        )


class CreateOrderForm(OrderForm):

    class Meta:
        model = Order
        fields = (
            "img",
            "title",
            "url",
            "order_price",
            "customer",
            "purchase"
        )


class CreatePurchaseOrderForm(OrderForm):

    class Meta:
        model = Order
        fields = (
            "img",
            "title",
            "url",
            "order_price",
            "customer"
        )
        widgets = {"img": forms.HiddenInput()}
        labels = {"img": ""}


class CreatePurchaseCustomerOrderForm(OrderForm):

    class Meta:
        model = Order
        fields = (
            "img",
            "title",
            "url",
            "order_price",
        )


class OrderSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_select_class = "form-select me-sm-2"
        default_input_class = "form-control me-sm-2"

        self.fields["customer"].widget.attrs['class'] = default_select_class
        self.fields["marketplace"].widget.attrs['class'] = default_select_class
        self.fields["status"].widget.attrs['class'] = default_select_class
        self.fields["query"].widget.attrs['class'] = default_input_class
        self.fields["purchase"].widget.attrs['class'] = default_select_class

    query = forms.CharField(
        label="Поиск",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Искать"})
    )
    customer = forms.ModelChoiceField(
        label="Клиент",
        queryset=Customer.objects.all(),
        empty_label="--- Клиент ---",
        required=False
    )
    status = forms.ChoiceField(
        label="Статус",
        choices=[("", "--- Статус ---")] + [
            (status.value, status.label) for status in Order.Status
        ],
        required=False
    )
    marketplace = forms.ModelChoiceField(
        label="Площадка",
        queryset=Marketplace.objects.all(),
        empty_label="--- Маркетплейс ---",
        required=False
    )
    purchase = forms.ModelChoiceField(
        label="Закупка",
        queryset=Purchase.objects.all(),
        empty_label="--- Закупка ---",
        required=False
    )