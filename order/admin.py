from django.contrib import admin

from order.models.marketplace import Marketplace
from .models.purchase import Purchase
from .models.customer import Customer
from .models.order import Order

from .constants import PROJECT_NAME, DEFAULT_NULL_VALUE


admin.site.site_header = PROJECT_NAME
admin.site.empty_value_display = DEFAULT_NULL_VALUE


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Class representing admin settings for a customer model"""

    list_display = ("name", "phone", "telegram_id")
    search_fields = ["name", "phone"]
    readonly_fields = ["created_at"]
    list_display_links = ["name", "phone"]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Class representing admin settings for a customer model"""

    list_display = ("title", "opened_date", "closed_date")
    list_filter = ["opened_date", "closed_date", "author"]
    search_fields = ["title"]
    readonly_fields = ["created_at"]
    list_display_links = ["title"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Class representing admin settings for a customer model"""

    list_display = ("display_img", "title", "price", "quantity", "purchase", "customer", "marketplace", "status")
    list_filter = ["purchase", "customer", "marketplace"]
    search_fields = ["title"]
    readonly_fields = ["created_at"]
    list_display_links = ["title"]

    @admin.display(description='Цена заказа/покупки (изменение)')
    def price(self, obj):
        buy_price = obj.buy_price if obj.buy_price else "---"
        differ = obj.buy_price - obj.order_price if obj.buy_price else "---"
        return f"{obj.order_price} / {buy_price} ({differ})"

    @admin.display(description='Статус')
    def status(self, obj):
        return obj.status

    @admin.display(description='Изображение товара')
    def display_img(self, obj):
        """Custom field display_logo"""
        return obj.display_img

    # def link_to_customer(self, obj):
    #     link = reverse("admin:myapp_customer_change", args=[obj.customer.id])
    #     return format_html(
    #         '<a href="{}">{}</a>',
    #         link,
    #         obj.customer,
    #     )


admin.site.register(Marketplace)
