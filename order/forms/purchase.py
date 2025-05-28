from django import forms
from order.forms.base import BaseForm
from order.models.customer import Customer
from order.models.marketplace import Marketplace
from order.models.purchase import Purchase
from order.models.order import Order


class PurchaseInitialForm(BaseForm):

    class Meta:
        model = Purchase
        fields = ("title", "opened_date", "exchange")


class PurchaseEditForm(BaseForm):

    class Meta:
        model = Purchase
        fields = (
            "title",
            "opened_date",
            "closed_date",
            "weight",
            "dilivery_cost1",
            "dilivery_cost2",
            "other_expenses",
        )


class PurchaseCloseForm(BaseForm):

    class Meta:
        model = Purchase
        fields = ("closed_date", "weight", "dilivery_cost1", "dilivery_cost2", "other_expenses")


class PurchaseSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Искать"})
    )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        empty_label="--- Клиент ---",
        required=False
    )
    status = forms.ChoiceField(
        choices=[("", "--- Статус ---")] + [
            (status.value, status.label) for status in Order.Status
        ],
        required=False
    )
    marketplace = forms.ModelChoiceField(
        queryset=Marketplace.objects.all(),
        empty_label="--- Маркетплейс ---",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_select_class = "form-select me-sm-2"
        default_input_class = "form-control me-sm-2"

        self.fields["customer"].widget.attrs['class'] = default_select_class
        self.fields["marketplace"].widget.attrs['class'] = default_select_class
        self.fields["status"].widget.attrs['class'] = default_select_class
        self.fields["query"].widget.attrs['class'] = default_input_class
