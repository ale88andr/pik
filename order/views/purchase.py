from django.shortcuts import render, get_object_or_404, redirect
from django.forms import model_to_dict
from django.db.models import Sum, Count
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from app.services import export_data_to_excel, export_to_excel
from app.utils import is_search_form_filled
from order.constants import PURCHASES
from order.forms.order import CreatePurchaseOrderForm
from order.forms.purchase import PurchaseInitialForm, PurchaseEditForm, PurchaseCloseForm, PurchaseSearchForm
from order.forms.search import SearchForm
from order.models.customer import Customer
from order.models.order import Order
from order.models.purchase import Purchase


PAGE_SECTION_URL = "purchases"


def list(request):
    form = SearchForm()
    query = request.GET.get("query")
    sort = request.GET.get("sort", "-created_at")

    if query:
        form = SearchForm(request.GET)
        if form.is_valid():
            search_query = form.cleaned_data["query"]
            orders = Purchase.objects.search(query=search_query)
    else:
        orders = Purchase.objects.prefetch_related("purchase_orders").annotate(
            num_of_customers=Count("purchase_orders__customer_id", distinct=True),
            cost_of_order_price=Sum("purchase_orders__order_price"),
            sum_of_weight=Sum("purchase_orders__weight"),
            num_of_orders=Count("purchase_orders")
        )

    return render(
        request,
        "purchase/list.html",
        {
            "form": form,
            "search_query": query,
            "records": orders.order_by(sort),
            "total": orders.count(),
            "page_section": PURCHASES,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Список закупок"
        }
    )


def detail(request, pk):
    search_form = PurchaseSearchForm(request.GET)
    purchase_customers = Customer.objects.distinct().filter(
        customer_orders__purchase_id=pk
    )
    
    search_form.fields["customer"].queryset = purchase_customers

    is_form_filled = is_search_form_filled(request, search_form.fields)
    search_orders = None
    sort = request.GET.get("sort", "created_at")

    if is_form_filled and search_form.is_valid():
        search_orders = Order.objects

        search = search_form.cleaned_data["query"]
        customer_id = search_form.cleaned_data["customer"]
        marketplace_id = search_form.cleaned_data["marketplace"]
        status = int(search_form.cleaned_data["status"]) if search_form.cleaned_data["status"] else None

        if search:
            search_orders = search_orders.search(query=search)

        if customer_id:
            search_orders = search_orders.filter(customer=customer_id)

        if marketplace_id:
            search_orders = search_orders.filter(marketplace=marketplace_id)

        if status is not None:
            search_orders = search_orders.filter(status=status)

        search_orders = search_orders.filter(purchase=pk)

    purchase = get_object_or_404(Purchase, pk=pk)
    orders = purchase.purchase_orders.select_related("customer", "marketplace").all()
    orders_info = purchase.purchase_orders.aggregate(
        total_amount=Sum("order_price"),
        number_of_customers=Count("customer_id", distinct=True),
        number_of_orders=Count("pk", distinct=True),
        orders_weight=Sum("weight"),
    )

    total = orders_info.get("total_amount", 0) or 0

    total_amount_rub = round(total * purchase.exchange, 2)
    total_tax_amount = sum(order.calculate_difference_tax() for order in orders)
    total_dif_amount = sum(order.get_difference for order in orders)
    total_profit = total_tax_amount + total_dif_amount - purchase.other_expenses

    records = search_orders if search_orders or is_form_filled else orders

    # Charts

    statuses = orders.values("status").annotate(total=Count("id"))

    status_chart_labels = [Order.Status.labels[obj["status"]] for obj in statuses]
    status_chart_values = [obj["total"] for obj in statuses]

    customers = orders.values("customer__name", "customer__id").annotate(orders=Count("id"))

    customer_chart_labels = [obj["customer__name"] for obj in customers]
    customer_chart_values = [obj["orders"] for obj in customers]
    
    records = records.order_by(sort)
    total = records.count()
    
    # Pagination
    
    page_num = request.GET.get('page', 1)
    paginator = Paginator(records, 20)

    try:
        records = paginator.page(page_num)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    return render(
        request,
        "purchase/detail.html",
        {
            "purchase": purchase,
            "purchase_customers": customers,
            "records": records,
            "total_records": total,
            "records_info": orders_info,
            "total_amount_rub": total_amount_rub,
            "total_tax_amount": total_tax_amount,
            "total_dif_amount": total_dif_amount,
            "total_profit": total_profit,
            "form": search_form,
            "current_page": records.number - 1,
            "page_section": PURCHASES,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": purchase.title,
            "status_chart_values": status_chart_values,
            "status_chart_labels": status_chart_labels,
            "customer_chart_labels": customer_chart_labels,
            "customer_chart_values": customer_chart_values
        }
    )


def create(request):
    if request.method == "POST":
        form = PurchaseInitialForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return redirect("purchases")
    else:
        form = PurchaseInitialForm()

    return render(
        request,
        "purchase/form.html",
        {
            "form": form,
            "page_section": PURCHASES,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Создание новой закупки"
        }
    )


def create_purchase_order(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(Purchase, id=pk)
        form = CreatePurchaseOrderForm(request.POST, files=request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            obj.purchase_orders.add(order, bulk=False)

            messages.success(request, f"Заказ '{order.title}' оформлен")

            if "add_another" in request.POST:
                return redirect("create-purchase-order", pk=pk)

            return redirect("purchase", pk=obj.pk)
        else:
            messages.error(request, "Возникли ошибки при заполнении формы, исправте их!")
    else:
        form = CreatePurchaseOrderForm()

    return render(
        request,
        "order/form.html",
        {
            "form": form,
            "is_new": True,
            "page_section": PURCHASES,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Добавление нового заказа"
        }
    )


def edit(request, pk):
    obj = get_object_or_404(Purchase, pk=pk)

    if request.method == "POST":
        form = PurchaseEditForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()

            messages.success(request, "Данные закупки обновлены!")
            return redirect("purchase", pk=obj.pk)
    else:
        form = PurchaseEditForm(model_to_dict(obj))

    return render(
        request,
        "purchase/form.html",
        {
            "form": form,
            "page_section": PURCHASES,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Редактирование данных закупки"
        }
    )


def delete(request, pk):
    customer = get_object_or_404(Purchase, pk=pk)
    customer.delete()
    return redirect("purchases")


def export_purchase_to_excel(request, pk):

    # Query the Person model to get all records
    purchase = get_object_or_404(Purchase, pk=pk)
    purchase_orders = purchase.purchase_orders.order_by("customer_id")

    response = export_data_to_excel(purchase.title, purchase_orders)

    return response


def export_purchase_tracknum_to_excel(request, pk):
    # Query the Person model to get all records
    purchase = get_object_or_404(Purchase, pk=pk)
    purchase_orders = purchase.purchase_orders.order_by("customer_id")
    header = ["Наименование", "Трек номер"]
    data = [order.export_data_for_cargo for order in purchase_orders]

    response = export_to_excel(
        f"{purchase.title} - трек номера",
        data,
        header
    )

    return response
