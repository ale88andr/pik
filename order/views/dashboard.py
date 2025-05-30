from django.shortcuts import render
from django.db.models import Sum, Count

from order.models.order import Order
from order.models.purchase import Purchase


def index(request):
    
    purchases = Purchase.objects.prefetch_related("purchase_orders").annotate(
        num_of_customers=Count("purchase_orders__customer_id", distinct=True),
        cost_of_order_price=Sum("purchase_orders__order_price"),
        num_of_orders=Count("purchase_orders")
    ).order_by("created_at")
    
    purchases_list = [p.title for p in purchases]
    purchases_num_of_orders_list = [p.num_of_orders for p in purchases]
    purchases_num_of_customers_list = [p.num_of_customers for p in purchases]
    cost_of_order_price_list = [float(round(p.cost_of_order_price * p.exchange, 2)) for p in purchases]
    
    orders = Order.objects.all().order_by("-created_at")[:15]
    
    return render(
        request,
        "dashboard/index.html",
        {
            "orders": orders,
            "purchases": purchases.filter(closed_date=None),
            "purchases_list": purchases_list,
            "purchases_num_of_orders_list": purchases_num_of_orders_list,
            "purchases_num_of_customers_list": purchases_num_of_customers_list,
            "cost_of_order_price_list": cost_of_order_price_list,
            "page_title": "Панель",
            "page_section": "Обзор",
        }
    )