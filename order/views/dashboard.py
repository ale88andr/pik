from django.shortcuts import render
from django.db.models import Sum, Count

from order.constants import DASHBOARD_ORD_LIMIT, DASHBOARD_SECTION, DASHBOARD_TITLE
from order.models.order import Order
from order.models.purchase import Purchase


def index(request):

    purchases = Purchase.objects.prefetch_related("purchase_orders").annotate(
        num_of_customers=Count("purchase_orders__customer_id", distinct=True),
        cost_of_order_price=Sum("purchase_orders__order_price"),
        num_of_orders=Count("purchase_orders")
    ).order_by("created_at")

    purchases_list = purchases.values_list("title", flat=True)
    purchases_num_of_orders_list = purchases.values_list("num_of_orders", flat=True)
    purchases_num_of_customers_list = purchases.values_list("num_of_customers", flat=True)
    cost_of_order_price_list = [
        float(round(p.cost_of_order_price * p.exchange, 2)) for p in purchases
    ]

    orders = Order.objects.order_by("-created_at")[:DASHBOARD_ORD_LIMIT]
    
    context = {
        "orders": orders,
        "purchases": purchases.filter(closed_date=None).order_by("-created_at"),
        "purchases_list": list(purchases_list),
        "purchases_num_of_orders_list": list(purchases_num_of_orders_list),
        "purchases_num_of_customers_list": list(purchases_num_of_customers_list),
        "cost_of_order_price_list": cost_of_order_price_list,
        "page_title": DASHBOARD_TITLE,
        "page_section": DASHBOARD_SECTION,
    }

    return render(request, "dashboard/index.html", context)
