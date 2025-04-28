from django import forms

from order.forms.base import BaseForm
from order.models.order import Order

class OrderForm(BaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_select_class = "form-select mb-3"
        default_checkbox_class = "form-check-input mb-3"

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


class CreateOrderForm(OrderForm):

    class Meta:
        model = Order
        fields = (
            "title",
            "url",
            "img",
            "quantity",
            "order_price",
            "buy_price",
            "exchange",
            "customer",
            "purchase",
            "marketplace"
        )


class CreatePurchaseOrderForm(OrderForm):

    class Meta:
        model = Order
        fields = (
            "title",
            "url",
            "img",
            "quantity",
            "order_price",
            "exchange",
            "customer"
        )
