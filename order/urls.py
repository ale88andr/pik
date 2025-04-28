from django.urls import path
from .views import customer
from .views import order
from .views import purchase


urlpatterns = [
    # customers
    path('customers', customer.list, name="customers"),
    path('customers/<int:pk>/edit', customer.edit, name='customer_edit'),
    path('customers/<int:pk>/delete', customer.delete, name='customer_delete'),
    path('customers/<int:pk>/', customer.detail, name='customer'),
    path('customers/new/', customer.create, name='customer_new'),

    # orders
    path('orders', order.list, name="orders"),
    path('orders/<int:pk>/edit', order.edit, name='order_edit'),
    path('orders/<int:pk>/delete', order.delete, name='order_delete'),
    path('orders/<int:pk>/', order.detail, name='order'),
    path('orders/new/', order.create, name='create-order'),

    # purchases
    path('purchases', purchase.list, name="purchases"),
    path('purchases/<int:pk>/edit', purchase.edit, name="edit-purchase"),
    path('purchases/<int:pk>/delete', purchase.delete, name="delete-purchase"),
    path('purchases/<int:pk>/new-order', purchase.create_purchase_order, name="create-purchase-order"),
    path('purchases/<int:pk>/', purchase.detail, name="purchase"),
    path('purchases/new/', purchase.create, name="create-purchase"),
]
