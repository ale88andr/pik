from django.urls import path, include

from order.views import dashboard
from .views import customer
from .views import order
from .views import purchase

# Customer routes
customer_patterns = [
    path("", customer.index, name="customers"),
    path("<int:pk>/edit", customer.edit, name="customer-edit"),
    path("<int:pk>/delete", customer.delete, name="customer-delete"),
    path("<int:pk>/", customer.detail, name="customer"),
    path(
        "<int:pk>/purchase/<int:purchase_pk>/export/xls",
        customer.export_purchase_to_excel,
        name="customer-purchase-xls",
    ),
    path(
        "<int:pk>/purchase/<int:purchase_pk>/new-order",
        customer.create_order,
        name="customer-new-order",
    ),
    path(
        "<int:pk>/purchase/<int:purchase_pk>",
        customer.purchase,
        name="customer-purchase",
    ),
    path("new/", customer.create, name="customer-new"),
]

# Order routes
order_patterns = [
    path("", order.list, name="orders"),
    path("<int:pk>/edit", order.edit, name="order-edit"),
    path("<int:pk>/buy", order.buy, name="order-buy"),
    path("<int:pk>/set-track", order.set_track_num, name="order-set-track"),
    path("<int:pk>/delivered", order.set_delivered, name="order-set-delivered"),
    path("<int:pk>/arrived", order.set_arrived, name="order-set-arrived"),
    path("<int:pk>/delete", order.delete, name="order-delete"),
    path("<int:pk>/", order.detail, name="order"),
    path("new/", order.create, name="order-new"),
]

# Purchase routes
purchase_patterns = [
    path("", purchase.list, name="purchases"),
    path("<int:pk>/edit", purchase.edit, name="purchase-edit"),
    path("<int:pk>/delete", purchase.delete, name="purchase-delete"),
    path(
        "<int:pk>/new-order",
        purchase.create_purchase_order,
        name="purchase-new-order",
    ),
    path("<int:pk>/", purchase.detail, name="purchase"),
    path("new/", purchase.create, name="purchase-new"),
    path("<int:pk>/export/xls", purchase.export_purchase_to_excel, name="purchase-xls"),
    path(
        "<int:pk>/cargo/xls",
        purchase.export_purchase_tracknum_to_excel,
        name="purchase-cargo-xls",
    ),
]

urlpatterns = [
    path("customers/", include(customer_patterns)),
    path("orders/", include(order_patterns)),
    path("purchases/", include(purchase_patterns)),
    path("", dashboard.index, name="dashboard"),
]
