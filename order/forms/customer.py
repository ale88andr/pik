from django import forms

from order.models.customer import Customer

class CustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control mb-3'

    class Meta:
        model = Customer
        fields = ("name", "phone", "telegram_id", "tax")
