from django.urls import path

from order.views import dashboard
from .views import customer
from .views import order
from .views import purchase


urlpatterns = [
    # customers
    path('customers', customer.index, name="customers"),
    path('customers/<int:pk>/edit', customer.edit, name='customer_edit'),
    path('customers/<int:pk>/delete', customer.delete, name='customer_delete'),
    path('customers/<int:pk>/', customer.detail, name='customer'),
    path('customers/<int:pk>/purchase/<int:purchase_pk>/export/xls', customer.export_purchase_to_excel, name='customer-purchase-xls2'),
    path('customers/<int:pk>/purchase/<int:purchase_pk>/new-order', customer.create_order, name='create-customer-order'),
    path('customers/<int:pk>/purchase/<int:purchase_pk>', customer.purchase, name='customer-purchase'),
    path('customers/new/', customer.create, name='customer_new'),

    # orders
    path('orders', order.list, name="orders"),
    path('orders/<int:pk>/edit', order.edit, name='order_edit'),
    path('orders/<int:pk>/buy', order.buy, name='order-buy'),
    path('orders/<int:pk>/set-track', order.set_track_num, name='order-set-track'),
    path('orders/<int:pk>/delivered', order.set_delivered, name='order-set-delivered'),
    path('orders/<int:pk>/arrived', order.set_arrived, name='order-set-arrived'),
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
    path('purchases/<int:pk>/export/xls', purchase.export_purchase_to_excel, name='purchase-xls'),
    path('purchases/<int:pk>/cargo/xls', purchase.export_purchase_tracknum_to_excel, name='purchase-cargo-xls'),

    # dashboard
    path('', dashboard.index, name="dashboard"),
]
